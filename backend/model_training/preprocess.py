import os
import re
import ast
import pandas as pd
from typing import List, Dict, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_python_files(codenet_dir: str) -> pd.DataFrame:
    """
    Extract Python files from CodeNetPy dataset
    
    Args:
        codenet_dir: Directory containing the CodeNetPy dataset
        
    Returns:
        DataFrame with code samples and metadata
    """
    data = []
    
    try:
        for root, _, files in os.walk(codenet_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    # Extract problem ID from directory structure if available
                    problem_id = os.path.basename(os.path.dirname(file_path))
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                            
                        # Basic validation - exclude very small snippets
                        if len(code) < 10:
                            continue
                            
                        # Get status information if available (correct/incorrect)
                        status_file = os.path.join(os.path.dirname(file_path), 'status.txt')
                        status = None
                        if os.path.exists(status_file):
                            with open(status_file, 'r') as f:
                                status = f.read().strip()
                        
                        data.append({
                            'file_path': file_path,
                            'problem_id': problem_id,
                            'code': code,
                            'status': status,
                            'file_size': len(code)
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {str(e)}")
        
        return pd.DataFrame(data)
    
    except Exception as e:
        logger.error(f"Error extracting Python files: {str(e)}")
        return pd.DataFrame()

def analyze_syntax_errors(code: str) -> List[str]:
    """
    Identify syntax errors in Python code
    
    Args:
        code: Python code snippet
        
    Returns:
        List of syntax error messages
    """
    errors = []
    
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}")
    
    return errors

def identify_common_logical_errors(code: str) -> List[str]:
    """
    Identify common logical errors in Python code
    
    Args:
        code: Python code snippet
        
    Returns:
        List of logical error messages
    """
    errors = []
    
    # Check for bare except
    if re.search(r'except\s*:', code) and not re.search(r'except\s*Exception', code):
        errors.append("Bare 'except:' blocks found. Consider handling specific exceptions.")
    
    # Check for potential infinite loops
    if re.search(r'while\s+True:', code) and not re.search(r'break', code):
        errors.append("Potential infinite loop: 'while True' without a 'break' statement.")
    
    # Check for variable shadowing of built-ins
    if re.search(r'\b(str|list|dict|set|int|float|bool|tuple|type)\s*=', code):
        errors.append("Overwriting built-in type names (str, list, etc.) can lead to unexpected behavior.")
    
    # Check for unused variables
    variable_definitions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code)
    for var in variable_definitions:
        if var != '_' and code.count(var) == 1:
            errors.append(f"Variable '{var}' is defined but never used.")
    
    # Check for mutable default arguments
    if re.search(r'def\s+\w+\s*\([^)]*=\s*\[\s*\][^)]*\):', code):
        errors.append("Using mutable default arguments (empty list) can lead to unexpected behavior.")
    
    return errors

def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare and label dataset for training
    
    Args:
        df: DataFrame with code samples
        
    Returns:
        Processed DataFrame with error labels
    """
    # Add syntactic and logical error columns
    df['syntax_errors'] = df['code'].apply(analyze_syntax_errors)
    df['has_syntax_error'] = df['syntax_errors'].apply(lambda x: len(x) > 0)
    
    df['logical_errors'] = df['code'].apply(identify_common_logical_errors)
    df['has_logical_error'] = df['logical_errors'].apply(lambda x: len(x) > 0)
    
    # Create binary labels
    df['has_error'] = df.apply(lambda row: row['has_syntax_error'] or row['has_logical_error'], axis=1)
    
    # Create multi-class label
    df['error_type'] = df.apply(
        lambda row: 'syntax' if row['has_syntax_error'] else ('logical' if row['has_logical_error'] else 'none'), 
        axis=1
    )
    
    return df

def split_dataset(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split dataset into training and testing sets
    
    Args:
        df: DataFrame with labeled code samples
        test_size: Proportion of data to use for testing
        
    Returns:
        Training and testing DataFrames
    """
    from sklearn.model_selection import train_test_split
    
    # Use stratified sampling to maintain class balance
    train_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        stratify=df['error_type'],
        random_state=42
    )
    
    return train_df, test_df
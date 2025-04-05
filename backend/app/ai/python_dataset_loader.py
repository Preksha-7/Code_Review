import os
import pandas as pd
import logging
from typing import List, Dict, Tuple, Optional
import json
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeNetPyLoader:
    """Loader for the CodeNetPy dataset for Python error detection training"""
    
    def __init__(self, dataset_path: str):
        """
        Initialize the dataset loader
        
        Args:
            dataset_path (str): Path to the CodeNetPy dataset directory
        """
        self.dataset_path = os.path.join("data", "Python", "problem_descriptions")
        self.metadata = None
        self.code_pairs = None
        
    def load_metadata(self) -> Dict:
        """
        Load dataset metadata
        
        Returns:
            Dict: Dataset metadata
        """
        try:
            metadata_path = os.path.join(self.dataset_path, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata: {len(self.metadata)} entries")
                return self.metadata
            else:
                logger.warning(f"Metadata file not found at {metadata_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return {}
    
    def load_code_pairs(self) -> pd.DataFrame:
        """
        Load code pairs from the dataset
        
        Returns:
            pd.DataFrame: DataFrame containing buggy and fixed code pairs
        """
        try:
            pairs_path = os.path.join(self.dataset_path, "code_pairs.csv")
            if os.path.exists(pairs_path):
                self.code_pairs = pd.read_csv(pairs_path)
                logger.info(f"Loaded {len(self.code_pairs)} code pairs")
                return self.code_pairs
            else:
                # Try to find alternative data files
                data_files = [f for f in os.listdir(self.dataset_path) 
                             if f.endswith('.csv') or f.endswith('.jsonl')]
                
                if data_files:
                    # Load the first available data file
                    first_file = os.path.join(self.dataset_path, data_files[0])
                    if first_file.endswith('.csv'):
                        self.code_pairs = pd.read_csv(first_file)
                    else:
                        # Handle JSONL format
                        data = []
                        with open(first_file, 'r') as f:
                            for line in f:
                                data.append(json.loads(line))
                        self.code_pairs = pd.DataFrame(data)
                    
                    logger.info(f"Loaded {len(self.code_pairs)} entries from {data_files[0]}")
                    return self.code_pairs
                else:
                    logger.error(f"No data files found in {self.dataset_path}")
                    return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading code pairs: {str(e)}")
            return pd.DataFrame()
    
    def preprocess_data(self) -> Tuple[List[str], List[str], List[str]]:
        """
        Preprocess data for training error detection models
        
        Returns:
            Tuple: Lists of buggy code, fixed code, and error messages
        """
        if self.code_pairs is None:
            self.load_code_pairs()
            
        if self.code_pairs.empty:
            logger.error("No code pairs available for preprocessing")
            return [], [], []
            
        buggy_code = []
        fixed_code = []
        error_messages = []
        
        # Determine column names (handle dataset variations)
        buggy_col = next((col for col in self.code_pairs.columns 
                         if 'buggy' in col.lower() or 'wrong' in col.lower()), None)
        fixed_col = next((col for col in self.code_pairs.columns 
                         if 'fixed' in col.lower() or 'correct' in col.lower() 
                         or 'solution' in col.lower()), None)
        error_col = next((col for col in self.code_pairs.columns 
                         if 'error' in col.lower() or 'exception' in col.lower()), None)
        
        if not buggy_col or not fixed_col:
            # Try to infer columns based on consecutive submissions
            if 'submission_id' in self.code_pairs.columns and 'code' in self.code_pairs.columns:
                # Sort by submission ID/timestamp
                sorted_df = self.code_pairs.sort_values('submission_id')
                
                for i in range(len(sorted_df)-1):
                    if sorted_df.iloc[i]['status'].lower() in ['wrong', 'error', 'failed']:
                        if sorted_df.iloc[i+1]['status'].lower() in ['correct', 'accepted', 'passed']:
                            buggy_code.append(sorted_df.iloc[i]['code'])
                            fixed_code.append(sorted_df.iloc[i+1]['code'])
                            error_msg = sorted_df.iloc[i].get('error_message', '')
                            error_messages.append(error_msg if error_msg else 'Unknown error')
            else:
                logger.error("Could not determine column names for code pairs")
                return [], [], []
        else:
            # Use determined column names
            buggy_code = self.code_pairs[buggy_col].tolist()
            fixed_code = self.code_pairs[fixed_col].tolist()
            
            if error_col and error_col in self.code_pairs.columns:
                error_messages = self.code_pairs[error_col].tolist()
            else:
                # Extract error info from diffs or attempt to infer errors
                error_messages = self._infer_errors(buggy_code, fixed_code)
        
        logger.info(f"Preprocessed {len(buggy_code)} code pairs")
        return buggy_code, fixed_code, error_messages
    
    def _infer_errors(self, buggy_code: List[str], fixed_code: List[str]) -> List[str]:
        """
        Infer error types from code differences
        
        Args:
            buggy_code (List[str]): List of buggy code snippets
            fixed_code (List[str]): List of fixed code snippets
            
        Returns:
            List[str]: Inferred error messages
        """
        error_messages = []
        common_python_errors = {
            r"indentation": "IndentationError",
            r"unexpected indent": "IndentationError",
            r"invalid syntax": "SyntaxError",
            r"undefined|not defined": "NameError",
            r"object has no attribute": "AttributeError",
            r"out of range": "IndexError",
            r"division by zero": "ZeroDivisionError"
        }
        
        for i, (buggy, fixed) in enumerate(zip(buggy_code, fixed_code)):
            # Analyze differences
            if buggy == fixed:
                error_messages.append("No error detected")
                continue
                
            # Try to infer error type from common patterns
            error_type = "Unknown error"
            
            # Check indentation differences
            if len(buggy.split('\n')) == len(fixed.split('\n')):
                if any(len(b.rstrip()) != len(f.rstrip()) for b, f in 
                      zip(buggy.split('\n'), fixed.split('\n'))):
                    error_type = "IndentationError"
            
            # Check for missing colons in function/loop definitions
            if re.search(r'(def|if|for|while|class)\s+\w+[^:]*$', buggy, re.MULTILINE):
                if re.search(r'(def|if|for|while|class)\s+\w+[^:]*:$', fixed, re.MULTILINE):
                    error_type = "SyntaxError: missing colon"
            
            # Check for undefined variables
            buggy_vars = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', buggy))
            fixed_vars = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', fixed))
            
            # If fixed has more variable definitions
            added_vars = fixed_vars - buggy_vars
            if added_vars:
                for var in added_vars:
                    if re.search(fr'\b{var}\s*=', fixed) and re.search(fr'\b{var}\b', buggy):
                        error_type = f"NameError: variable '{var}' used before definition"
                        break
            
            error_messages.append(error_type)
        
        return error_messages
            
    def get_training_data(self) -> Dict:
        """
        Get processed data ready for training
        
        Returns:
            Dict: Training data with buggy code, fixed code, and errors
        """
        buggy_code, fixed_code, error_messages = self.preprocess_data()
        
        return {
            "buggy_code": buggy_code,
            "fixed_code": fixed_code,
            "error_messages": error_messages,
            "count": len(buggy_code)
        }
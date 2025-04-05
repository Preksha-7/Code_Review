import os
import logging
import joblib
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import ast
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model directories
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Define paths for different models
ERROR_DETECTOR_PATH = os.path.join(MODEL_DIR, "python_error_detector.joblib")
ERROR_CLASSIFIER_PATH = os.path.join(MODEL_DIR, "python_error_classifier.joblib")
ERROR_LOCATION_PATH = os.path.join(MODEL_DIR, "python_error_locator.joblib")

# Load models if they exist
try:
    error_detector = joblib.load(ERROR_DETECTOR_PATH) if os.path.exists(ERROR_DETECTOR_PATH) else None
    error_classifier = joblib.load(ERROR_CLASSIFIER_PATH) if os.path.exists(ERROR_CLASSIFIER_PATH) else None
    error_locator = joblib.load(ERROR_LOCATION_PATH) if os.path.exists(ERROR_LOCATION_PATH) else None
    
    if error_detector:
        logger.info("Python error detection model loaded successfully")
    if error_classifier:
        logger.info("Python error classification model loaded successfully")
    if error_locator:
        logger.info("Python error location model loaded successfully")
        
except Exception as e:
    logger.error(f"Error loading Python error models: {str(e)}")
    error_detector = None
    error_classifier = None
    error_locator = None

def extract_python_features(code: str) -> Dict[str, Union[float, int]]:
    """
    Extract features from Python code for error detection/classification
    
    Args:
        code (str): Python code snippet
        
    Returns:
        Dict: Feature dictionary
    """
    features = {}
    
    # Basic metrics
    features['code_length'] = len(code)
    features['line_count'] = code.count('\n') + 1
    
    # Syntax elements
    features['indentation_count'] = sum(1 for line in code.split('\n') if line.startswith(' ') or line.startswith('\t'))
    features['colon_count'] = code.count(':')
    features['def_count'] = len(re.findall(r'\bdef\s+\w+', code))
    features['class_count'] = len(re.findall(r'\bclass\s+\w+', code))
    
    # Control flow
    features['if_count'] = len(re.findall(r'\bif\b', code))
    features['else_count'] = len(re.findall(r'\belse\b', code))
    features['for_count'] = len(re.findall(r'\bfor\b', code))
    features['while_count'] = len(re.findall(r'\bwhile\b', code))
    features['try_count'] = len(re.findall(r'\btry\b', code))
    features['except_count'] = len(re.findall(r'\bexcept\b', code))
    
    # Variables and operators
    features['assignment_count'] = code.count('=') - code.count('==') - code.count('<=') - code.count('>=') - code.count('!=')
    features['plus_count'] = code.count('+')
    features['minus_count'] = code.count('-')
    features['mult_count'] = code.count('*')
    features['div_count'] = code.count('/')
    
    # Common Python features
    features['list_comp_count'] = len(re.findall(r'\[[^]]*\s+for\s+', code))
    features['import_count'] = len(re.findall(r'\bimport\b', code))
    features['return_count'] = len(re.findall(r'\breturn\b', code))
    
    # Advanced features - using AST if possible
    try:
        tree = ast.parse(code)
        
        # Count variable names
        variables = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variables.add(node.id)
        
        features['unique_var_count'] = len(variables)
        features['reserved_names_as_var'] = sum(1 for v in variables if v in ['list', 'dict', 'str', 'int', 'float', 'tuple', 'set', 'type'])
        
        # Function calls
        func_calls = [node.func.id for node in ast.walk(tree) 
                     if isinstance(node, ast.Call) and hasattr(node.func, 'id')]
        features['func_call_count'] = len(func_calls)
        
        # No syntax errors since we could parse it
        features['has_syntax_error'] = 0
        
    except SyntaxError:
        # Failed to parse - likely has syntax errors
        features['unique_var_count'] = len(set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)))
        features['reserved_names_as_var'] = 0  # Cannot determine accurately
        features['func_call_count'] = len(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code))
        features['has_syntax_error'] = 1
    
    # Code style features
    features['empty_line_ratio'] = sum(1 for line in code.split('\n') if line.strip() == '') / max(1, features['line_count'])
    features['comment_ratio'] = sum(1 for line in code.split('\n') if line.strip().startswith('#')) / max(1, features['line_count'])
    
    return features

def detect_python_errors(code: str) -> Dict:
    """
    Detect and classify errors in Python code using trained models
    
    Args:
        code (str): Python code snippet
        
    Returns:
        Dict: Error detection results
    """
    # Start with syntax checking
    try:
        ast.parse(code)
        has_syntax_error = False
        syntax_error_msg = None
        syntax_error_line = None
    except SyntaxError as e:
        has_syntax_error = True
        syntax_error_msg = str(e)
        syntax_error_line = e.lineno
    except Exception as e:
        has_syntax_error = True
        syntax_error_msg = str(e)
        syntax_error_line = None
    
    # Use trained model for error detection if available
    error_probability = None
    error_type = None
    error_location = None
    potential_fixes = []
    
    if error_detector:
        try:
            # Extract features
            features = extract_python_features(code)
            
            # Convert to format expected by model
            feature_vector = [features[f] if f in features else 0.0 
                             for f in error_detector.feature_names_in_]
            
            # Predict error probability
            error_probability = float(error_detector.predict_proba([feature_vector])[0][1])
            
            # Classify error type if probability is high enough
            if error_probability > 0.5 and error_classifier:
                error_type_idx = error_classifier.predict([feature_vector])[0]
                error_types = ['SyntaxError', 'IndentationError', 'NameError', 
                              'TypeError', 'AttributeError', 'IndexError', 'Other']
                error_type = error_types[error_type_idx] if error_type_idx < len(error_types) else 'Other'
                
            # Locate error if possible
            if error_locator and has_syntax_error:
                lines = code.split('\n')
                line_features = []
                
                for i, line in enumerate(lines):
                    line_feat = {}
                    line_feat['line_num'] = i + 1
                    line_feat['line_length'] = len(line)
                    line_feat['indentation'] = len(line) - len(line.lstrip())
                    line_feat['has_colon'] = int(':' in line)
                    line_feat['line_position'] = (i + 1) / len(lines)
                    line_features.append(line_feat)
                
                if line_features:
                    # Convert to array expected by model
                    line_vectors = [[feat[f] if f in feat else 0.0 
                                   for f in error_locator.feature_names_in_]
                                   for feat in line_features]
                    
                    # Predict error line probabilities
                    line_probs = error_locator.predict_proba(line_vectors)
                    error_line_idx = np.argmax([p[1] for p in line_probs])
                    error_location = line_features[error_line_idx]['line_num']
                
        except Exception as e:
            logger.error(f"Error using ML models for detection: {str(e)}")
            traceback.print_exc()
    
    # Generate common fixes based on error type
    if has_syntax_error:
        # For syntax errors
        if "invalid syntax" in str(syntax_error_msg).lower():
            potential_fixes.append("Check for missing parentheses, brackets, or quotes")
            potential_fixes.append("Make sure all blocks (if, for, while, etc.) end with a colon")
        
        if "expected an indented block" in str(syntax_error_msg).lower():
            potential_fixes.append("Add indentation after statements ending with a colon")
        
        if "unexpected indent" in str(syntax_error_msg).lower():
            potential_fixes.append("Fix indentation to be consistent throughout the code")
    
    if error_type == "NameError" or (syntax_error_msg and "name" in str(syntax_error_msg).lower() and "is not defined" in str(syntax_error_msg).lower()):
        # Extract variable name if present in error message
        var_match = re.search(r"name '(\w+)' is not defined", str(syntax_error_msg) if syntax_error_msg else "")
        if var_match:
            var_name = var_match.group(1)
            potential_fixes.append(f"Define variable '{var_name}' before using it")
            potential_fixes.append(f"Check if '{var_name}' is misspelled")
        else:
            potential_fixes.append("Make sure all variables are defined before use")
    
    # Return detailed analysis
    return {
        "has_error": has_syntax_error or (error_probability and error_probability > 0.7),
        "syntax_error": has_syntax_error,
        "error_message": syntax_error_msg if has_syntax_error else None,
        "error_line": syntax_error_line or error_location,
        "error_probability": error_probability,
        "error_type": error_type or ("SyntaxError" if has_syntax_error else None),
        "potential_fixes": potential_fixes
    }

def train_error_detection_model(buggy_code: List[str], fixed_code: List[str], 
                              error_messages: List[str]) -> Dict:
    """
    Train machine learning models for Python error detection and classification
    
    Args:
        buggy_code (List[str]): Buggy code examples
        fixed_code (List[str]): Corresponding fixed code examples
        error_messages (List[str]): Error messages for the buggy code
        
    Returns:
        Dict: Training results
    """
    if len(buggy_code) == 0 or len(buggy_code) != len(fixed_code):
        return {
            "success": False,
            "message": "Invalid training data: missing or mismatched code pairs"
        }
    
    try:
        logger.info(f"Training Python error detection models with {len(buggy_code)} examples")
        
        # Prepare features
        X = []
        y_has_error = []  # Binary classification: has error or not
        y_error_type = []  # Multi-class: error type
        
        # Define error type mapping
        error_type_map = {
            'SyntaxError': 0,
            'IndentationError': 1,
            'NameError': 2,
            'TypeError': 3,
            'AttributeError': 4,
            'IndexError': 5,
            'Other': 6
        }
        
        # Extract features from all code pairs
        for i, (buggy, fixed, error_msg) in enumerate(zip(buggy_code, fixed_code, error_messages)):
            # Extract features
            features = extract_python_features(buggy)
                
            # Determine if code has an error (if buggy != fixed)
            has_error = buggy.strip() != fixed.strip()
            y_has_error.append(1 if has_error else 0)
            
            # Determine error type from error message
            error_type = 'Other'
            for err_type in error_type_map.keys():
                if err_type in error_msg:
                    error_type = err_type
                    break
            
            y_error_type.append(error_type_map.get(error_type, 6))  # Default to 'Other'
            
            # Add feature vector
            X.append([features[f] if f in features else 0.0 for f in sorted(features.keys())])
        
        # Split data
        X_train, X_test, y_train_error, y_test_error = train_test_split(
            X, y_has_error, test_size=0.2, random_state=42)
        
        # Train error detection model
        logger.info("Training error detection model...")
        detector = GradientBoostingClassifier(n_estimators=100, max_depth=5)
        detector.fit(X_train, y_train_error)
        detector.feature_names_in_ = sorted(features.keys())
        
        # Save model
        joblib.dump(detector, ERROR_DETECTOR_PATH)
        logger.info(f"Error detection model saved to {ERROR_DETECTOR_PATH}")
        
        # Evaluate on test set
        detector_accuracy = accuracy_score(y_test_error, detector.predict(X_test))
        logger.info(f"Error detection accuracy: {detector_accuracy:.4f}")
        
        # Train error type classifier if enough data
        if sum(y_has_error) > 50:  # Only train if we have enough error examples
            # Filter to only use error cases for error type classification
            error_indices = [i for i, has_err in enumerate(y_has_error) if has_err == 1]
            X_errors = [X[i] for i in error_indices]
            y_error_types = [y_error_type[i] for i in error_indices]
            
            if len(set(y_error_types)) > 1:  # Only if we have multiple error types
                # Split data
                X_train_type, X_test_type, y_train_type, y_test_type = train_test_split(
                    X_errors, y_error_types, test_size=0.2, random_state=42)
                
                logger.info("Training error classification model...")
                classifier = RandomForestClassifier(n_estimators=100)
                classifier.fit(X_train_type, y_train_type)
                classifier.feature_names_in_ = sorted(features.keys())
                
                # Save model
                joblib.dump(classifier, ERROR_CLASSIFIER_PATH)
                logger.info(f"Error classification model saved to {ERROR_CLASSIFIER_PATH}")
                
                # Evaluate
                classifier_accuracy = accuracy_score(y_test_type, classifier.predict(X_test_type))
                logger.info(f"Error type classification accuracy: {classifier_accuracy:.4f}")
                
                # Also make available globally
                global error_classifier
                error_classifier = classifier
            else:
                logger.warning("Not enough error type diversity for classification model")
        
        # Make model available globally
        global error_detector
        error_detector = detector
        
        # Optional: Train error locator model (more complex, skipped in basic implementation)
        
        return {
            "success": True,
            "detector_accuracy": detector_accuracy,
            "classifier_trained": error_classifier is not None,
            "models_path": MODEL_DIR
        }
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Training failed: {str(e)}"
        }
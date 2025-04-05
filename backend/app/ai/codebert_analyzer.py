from transformers import AutoTokenizer, RobertaForSequenceClassification
import torch
import re
import logging
import ast
import json
import os
from typing import List, Dict, Any, Tuple, Optional
import joblib
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the model with error handling
try:
    # Load the CodeBERT model once at startup
    MODEL_NAME = "microsoft/codebert-base"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.eval()  # Set to evaluation mode
    logger.info("CodeBERT model loaded successfully")
    
    # Path to additional ML models
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Load additional ML models if they exist
    QUALITY_MODEL_PATH = os.path.join(MODEL_DIR, "code_quality_model.joblib")
    LANGUAGE_DETECTOR_PATH = os.path.join(MODEL_DIR, "language_detector.joblib")
    
    quality_model = joblib.load(QUALITY_MODEL_PATH) if os.path.exists(QUALITY_MODEL_PATH) else None
    language_detector = joblib.load(LANGUAGE_DETECTOR_PATH) if os.path.exists(LANGUAGE_DETECTOR_PATH) else None
    
    if quality_model:
        logger.info("Code quality ML model loaded successfully")
    if language_detector:
        logger.info("Language detection ML model loaded successfully")
        
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    model = None
    tokenizer = None
    quality_model = None
    language_detector = None

def detect_language(code_snippet: str) -> str:
    """
    Detect programming language of the given code snippet
    
    Args:
        code_snippet (str): Code snippet to analyze
        
    Returns:
        str: Detected language identifier
    """
    # Use ML-based language detector if available
    if language_detector:
        try:
            detected_lang = language_detector.predict([code_snippet])[0]
            return detected_lang
        except Exception as e:
            logger.error(f"Error using ML language detector: {str(e)}")
    
    # Fallback: Basic heuristic language detection
    code = code_snippet.strip()
    
    # Python indicators
    if re.search(r'def\s+\w+\s*\([^)]*\)\s*:', code) or \
       re.search(r'import\s+\w+', code) or \
       re.search(r'from\s+\w+\s+import', code) or \
       re.search(r'print\s*\(', code):
        return "python"
    
    # JavaScript indicators
    if re.search(r'const\s+\w+\s*=', code) or \
       re.search(r'let\s+\w+\s*=', code) or \
       re.search(r'function\s+\w+\s*\(', code) or \
       re.search(r'console\.log', code):
        return "javascript"
    
    # C++ indicators
    if re.search(r'#include\s*<\w+>', code) or \
       re.search(r'int\s+main\s*\(\s*\)', code) or \
       re.search(r'std::', code) or \
       re.search(r'cout\s*<<', code):
        return "cpp"
    
    # Java indicators
    if re.search(r'public\s+class\s+\w+', code) or \
       re.search(r'public\s+static\s+void\s+main', code) or \
       re.search(r'System\.out\.print', code):
        return "java"
    
    # C# indicators
    if re.search(r'namespace\s+\w+', code) or \
       re.search(r'using\s+System;', code) or \
       re.search(r'Console\.Write', code):
        return "csharp"
    
    # Default to the most common language if can't detect
    return "python"

# Language-specific analyzers
def analyze_python(code_snippet):
    """Analyzes Python code for syntax and semantic issues"""
    issues = []
    
    # Check for syntax errors
    try:
        ast.parse(code_snippet)
    except SyntaxError as e:
        issues.append(f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}")
        return issues
    
    # Check for potential issues
    if "except:" in code_snippet and "pass" in code_snippet:
        issues.append("Bare 'except: pass' blocks found. Consider handling exceptions properly.")
    
    if re.search(r'print\([^)]*\)', code_snippet) and not re.search(r'print\([\'"]', code_snippet):
        issues.append("Print statements without descriptive strings may make debugging difficult.")
    
    # Check for variable naming issues
    if re.search(r'\b(str|list|dict|set|int|float|bool|tuple|type)\s*=', code_snippet):
        issues.append("Overwriting built-in type names (str, list, etc.) can lead to unexpected behavior.")
    
    # Check for potential infinite loops
    if re.search(r'while\s+True:', code_snippet) and not re.search(r'break', code_snippet):
        issues.append("Potential infinite loop: 'while True' without a 'break' statement.")
    
    # Check for unused variables
    variable_definitions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code_snippet)
    for var in variable_definitions:
        if var != '_' and code_snippet.count(var) == 1:
            issues.append(f"Variable '{var}' is defined but never used.")
    
    return issues

def analyze_javascript(code_snippet):
    """Analyzes JavaScript code for common issues"""
    issues = []
    
    # Check for missing semicolons
    lines = code_snippet.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}') and \
           not line.endswith(':') and not line.startswith('//') and not line.startswith('/*'):
            if not any(keyword in line for keyword in ['if', 'for', 'while', 'function', 'class', 'import', 'export']):
                issues.append(f"Line {i+1}: Missing semicolon at end of statement.")
    
    # Check for console.log statements
    if 'console.log' in code_snippet:
        issues.append("Console.log statements found. Remove them before production.")
    
    # Check for var instead of let/const
    if re.search(r'\bvar\b', code_snippet):
        issues.append("Using 'var' is discouraged. Consider using 'let' or 'const' instead.")
    
    # Check for potential undefined variables
    js_keywords = ['let', 'const', 'var', 'function', 'class', 'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'return']
    words = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code_snippet)
    for word in words:
        if word not in js_keywords and f"let {word}" not in code_snippet and f"const {word}" not in code_snippet and f"var {word}" not in code_snippet:
            if code_snippet.count(word) == 1 and re.search(fr'\b{word}\s*=', code_snippet):
                issues.append(f"Variable '{word}' might be used without being declared.")
    
    return issues

def analyze_java(code_snippet):
    """Analyzes Java code for common issues"""
    issues = []
    
    # Check for missing semicolons
    lines = code_snippet.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}') and \
           not line.startswith('//') and not line.startswith('/*') and not line.startswith('*'):
            if not any(keyword in line for keyword in ['if', 'for', 'while', 'class', 'interface', 'enum']):
                issues.append(f"Line {i+1}: Missing semicolon.")
    
    # Check for potential null pointer issues
    if 'null' in code_snippet and ('==' in code_snippet or '!=' in code_snippet):
        if not '.equals(' in code_snippet and re.search(r'if\s*\(.+?==.+?\)', code_snippet):
            issues.append("Potential null pointer issue: consider using Objects.equals() for null-safe comparisons.")
    
    # Check for public fields
    if re.search(r'public\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*;', code_snippet):
        issues.append("Public fields found. Consider using private fields with getters and setters.")
    
    # Check for empty catch blocks
    if re.search(r'catch\s*\([^)]+\)\s*{\s*}', code_snippet):
        issues.append("Empty catch blocks found. Consider handling exceptions properly.")
    
    return issues

def analyze_cpp(code_snippet):
    """Analyzes C++ code for common issues"""
    issues = []
    
    # Check for missing semicolons
    lines = code_snippet.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}') and \
           not line.startswith('//') and not line.startswith('/*'):
            if not any(keyword in line for keyword in ['if', 'for', 'while', 'class', 'struct', 'namespace', '#include']):
                issues.append(f"Line {i+1}: Missing semicolon.")
    
    # Check for language mismatches - Python syntax in C++
    if re.search(r'print\s*\(', code_snippet):
        issues.append("Python 'print()' function detected in C++ code. Use 'std::cout <<' instead.")
    
    if re.search(r'def\s+\w+\s*\(', code_snippet):
        issues.append("Python function definition syntax detected in C++ code.")
    
    # Check for missing include statements
    if re.search(r'cout|cin|string|vector|map', code_snippet) and not re.search(r'#include', code_snippet):
        issues.append("C++ standard library features used without corresponding #include directives.")
    
    # Check for using namespace std
    if re.search(r'using\s+namespace\s+std', code_snippet):
        issues.append("'using namespace std' is generally discouraged in C++ as it can lead to name collisions.")
    
    # Check for memory management issues
    if re.search(r'new\s+\w+', code_snippet) and not re.search(r'delete', code_snippet):
        issues.append("Potential memory leak: 'new' used without corresponding 'delete'.")
    
    return issues

def analyze_csharp(code_snippet):
    """Analyzes C# code for common issues"""
    issues = []
    
    # Check for missing semicolons
    lines = code_snippet.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}') and \
           not line.startswith('//') and not line.startswith('/*'):
            if not any(keyword in line for keyword in ['if', 'for', 'while', 'class', 'namespace']):
                issues.append(f"Line {i+1}: Missing semicolon.")
    
    # Check for language mismatches
    if re.search(r'print\s*\(', code_snippet):
        issues.append("Python 'print()' function detected in C# code. Use 'Console.WriteLine()' instead.")
    
    # Check for empty catch blocks
    if re.search(r'catch\s*\([^)]*\)\s*{\s*}', code_snippet):
        issues.append("Empty catch blocks found. Consider handling exceptions properly.")
    
    # Check for potential null reference issues
    if '== null' in code_snippet or '!= null' in code_snippet:
        issues.append("Consider using the null-conditional operator (?.), null-coalescing operator (??), or pattern matching for null checks.")
    
    return issues

def extract_code_features(code_snippet: str) -> Dict[str, float]:
    """
    Extract features from code for ML models
    
    Args:
        code_snippet (str): The code to analyze
        
    Returns:
        Dict[str, float]: Dictionary of code quality features
    """
    features = {}
    
    # Code complexity features
    features['code_length'] = len(code_snippet)
    features['line_count'] = code_snippet.count('\n') + 1
    features['comment_ratio'] = (code_snippet.count('#') + code_snippet.count('//') + 
                               code_snippet.count('/*')) / max(1, features['line_count'])
    
    # Variable features
    var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*='
    variables = re.findall(var_pattern, code_snippet)
    features['variable_count'] = len(variables)
    features['avg_var_name_length'] = sum(len(v) for v in variables) / max(1, len(variables))
    
    # Control structure features
    features['if_count'] = len(re.findall(r'\bif\b', code_snippet))
    features['loop_count'] = len(re.findall(r'\b(for|while)\b', code_snippet))
    features['function_count'] = len(re.findall(r'\b(def|function)\b', code_snippet))
    
    # Error markers
    features['error_marker_count'] = code_snippet.count('TODO') + code_snippet.count('FIXME')
    
    return features

def predict_quality_score(code_snippet: str, language: str) -> float:
    """
    Use ML model to predict code quality if available, otherwise use CodeBERT
    
    Args:
        code_snippet (str): Code to analyze
        language (str): Programming language
        
    Returns:
        float: Quality score between 0 and 1
    """
    if quality_model:
        try:
            # Extract features for ML model
            features = extract_code_features(code_snippet)
            
            # Add language as one-hot features
            languages = ['python', 'javascript', 'java', 'cpp', 'csharp']
            for lang in languages:
                features[f'is_{lang}'] = 1.0 if language == lang else 0.0
                
            # Convert features to numeric array
            feature_vector = np.array([[features[f] if f in features else 0.0 
                                      for f in quality_model.feature_names_in_]])
            
            # Predict quality score
            score = quality_model.predict_proba(feature_vector)[0][1]  # Probability of good code
            return float(score)
        except Exception as e:
            logger.error(f"Error using ML quality model: {str(e)}")
    
    # Fallback to CodeBERT prediction
    if model and tokenizer:
        try:
            inputs = tokenizer(code_snippet, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                prediction_score = torch.softmax(logits, dim=1)[0][1].item()  # Probability of "good code"
            return prediction_score
        except Exception as e:
            logger.error(f"Error in CodeBERT prediction: {str(e)}")
    
    # Default fallback score
    return 0.5

def analyze_code(code_snippet: str, language: str = "python", detect_lang: bool = True) -> dict:
    """
    Analyzes the given code snippet using CodeBERT, ML models, and language-specific heuristics.
    
    Args:
        code_snippet (str): The code snippet to analyze
        language (str): The programming language of the code (default: "python")
        detect_lang (bool): Whether to auto-detect language (default: True)
        
    Returns:
        dict: Code analysis results
    """
    if not code_snippet.strip():
        return {
            "prediction": 0.0,
            "overall_feedback": "No code provided for analysis.",
            "detailed_feedback": ["Please provide code to analyze."],
            "issues_count": 1,
            "syntax_errors": [],
            "logic_errors": [],
            "detected_language": None
        }
    
    # Auto-detect language if enabled
    detected_language = detect_language(code_snippet) if detect_lang else None
    
    # Check for language mismatch
    language_mismatch = detected_language and language.lower() != detected_language
    actual_language = detected_language if language_mismatch else language.lower()
    
    # Language-specific analysis
    language_specific_issues = []
    syntax_errors = []
    logic_errors = []
    
    try:
        if actual_language == "python":
            language_specific_issues = analyze_python(code_snippet)
        elif actual_language in ["javascript", "js"]:
            language_specific_issues = analyze_javascript(code_snippet)
        elif actual_language == "java":
            language_specific_issues = analyze_java(code_snippet)
        elif actual_language == "cpp":
            language_specific_issues = analyze_cpp(code_snippet)
        elif actual_language == "csharp":
            language_specific_issues = analyze_csharp(code_snippet)
        
        # Add language mismatch warning if detected
        if language_mismatch:
            mismatch_warning = f"Language mismatch detected: Code appears to be {detected_language}, but was submitted as {language}."
            language_specific_issues.insert(0, mismatch_warning)
            logic_errors.append(mismatch_warning)
    except Exception as e:
        logger.error(f"Error in language-specific analysis: {str(e)}")
        language_specific_issues = [f"Error analyzing code: {str(e)}"]
    
    # Classify issues into syntax errors and logic errors
    for issue in language_specific_issues:
        if "Language mismatch" in issue:
            continue  # Already added to logic errors
        elif "syntax" in issue.lower() or "missing" in issue.lower():
            syntax_errors.append(issue)
        else:
            logic_errors.append(issue)
    
    # Get quality prediction score
    prediction_score = predict_quality_score(code_snippet, actual_language)
    
    # Additional heuristic analysis
    feedback = []
    issues_found = 0
    
    # Check for common issues in any language
    if "import" not in code_snippet and len(code_snippet) > 100 and actual_language == "python":
        feedback.append("Consider adding necessary imports.")
        issues_found += 1
    
    if "  " in code_snippet:  # Double spaces
        feedback.append("Inconsistent spacing detected.")
        issues_found += 1
    
    # Handle language-specific issues
    for issue in language_specific_issues:
        feedback.append(issue)
        issues_found += 1
    
    # Check indentation and braces
    if code_snippet.count('{') != code_snippet.count('}') and actual_language in ["javascript", "js", "java", "c", "cpp", "csharp"]:
        feedback.append("Mismatched braces detected.")
        issues_found += 1
        syntax_errors.append("Mismatched braces detected.")
    
    # Check for hardcoded values
    if re.search(r'(password|secret|api_key|token)\s*=\s*[\'"](.*?)[\'"]', code_snippet, re.IGNORECASE):
        feedback.append("Hardcoded secrets detected. Consider using environment variables.")
        issues_found += 1
        logic_errors.append("Hardcoded secrets detected. Consider using environment variables.")
    
    # Generate overall feedback
    if syntax_errors:
        overall = "Syntax errors detected. Fix these issues before proceeding."
    elif language_mismatch:
        overall = f"Language mismatch: Code appears to be {detected_language}, but was submitted as {language}. Please select the correct language."
    elif prediction_score < 0.4 or issues_found > 2:
        overall = "Significant issues detected. Review recommended."
    elif prediction_score < 0.7 or issues_found > 0:
        overall = "Minor issues found. Consider the suggestions below."
    else:
        overall = "Code looks good! No major issues detected."
    
    if not feedback:
        feedback.append("No specific issues detected.")
    
    return {
        "prediction": prediction_score,
        "overall_feedback": overall,
        "detailed_feedback": feedback,
        "issues_count": issues_found,
        "syntax_errors": syntax_errors,
        "logic_errors": logic_errors,
        "detected_language": detected_language
    }

# ML training functions (to be called when collecting data)
def train_language_detector(code_samples: List[Tuple[str, str]]) -> None:
    """
    Train and save language detection model
    
    Args:
        code_samples: List of (code, language) tuples
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        
        # Extract code and labels
        code_snippets = [code for code, _ in code_samples]
        languages = [lang for _, lang in code_samples]
        
        # Create pipeline
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ('classifier', RandomForestClassifier(n_estimators=100))
        ])
        
        # Train model
        pipeline.fit(code_snippets, languages)
        
        # Save model
        joblib.dump(pipeline, LANGUAGE_DETECTOR_PATH)
        logger.info(f"Language detection model saved to {LANGUAGE_DETECTOR_PATH}")
        
        # Make available globally
        global language_detector
        language_detector = pipeline
        
    except Exception as e:
        logger.error(f"Error training language detection model: {str(e)}")

def train_quality_model(code_samples: List[Tuple[str, str, float, List[str]]]) -> None:
    """
    Train and save code quality prediction model
    
    Args:
        code_samples: List of (code, language, quality_score, issues) tuples
    """
    try:
        from sklearn.ensemble import GradientBoostingRegressor
        
        # Prepare training data
        X = []
        y = []
        
        for code, language, quality_score, _ in code_samples:
            # Extract features
            features = extract_code_features(code)
            
            # Add language as one-hot features
            languages = ['python', 'javascript', 'java', 'cpp', 'csharp']
            for lang in languages:
                features[f'is_{lang}'] = 1.0 if language == lang else 0.0
            
            # Convert to vector
            feature_vector = [features[f] for f in sorted(features.keys())]
            X.append(feature_vector)
            y.append(quality_score)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5)
        model.fit(X, y)
        
        # Save feature names
        model.feature_names_in_ = sorted(features.keys())
        
        # Save model
        joblib.dump(model, QUALITY_MODEL_PATH)
        logger.info(f"Code quality model saved to {QUALITY_MODEL_PATH}")
        
        # Make available globally
        global quality_model
        quality_model = model
        
    except Exception as e:
        logger.error(f"Error training code quality model: {str(e)}")
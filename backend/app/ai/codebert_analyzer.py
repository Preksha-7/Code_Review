from transformers import AutoTokenizer, RobertaForSequenceClassification
import torch
import re
import logging
import ast
import json

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
except Exception as e:
    logger.error(f"Error loading CodeBERT model: {str(e)}")
    model = None
    tokenizer = None

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

def analyze_code(code_snippet: str, language: str = "python") -> dict:
    """Analyzes the given code snippet using CodeBERT and language-specific heuristics."""
    
    if not model or not tokenizer:
        logger.error("CodeBERT model not initialized correctly")
        return {
            "prediction": 0.0,
            "overall_feedback": "Model initialization error. Using basic analysis only.",
            "detailed_feedback": ["Server configuration issue. Using basic analysis."],
            "issues_count": 1,
            "syntax_errors": [],
            "logic_errors": []
        }
    
    # Language-specific analysis
    language_specific_issues = []
    syntax_errors = []
    logic_errors = []
    
    try:
        if language.lower() == "python":
            language_specific_issues = analyze_python(code_snippet)
        elif language.lower() in ["javascript", "js"]:
            language_specific_issues = analyze_javascript(code_snippet)
        elif language.lower() == "java":
            language_specific_issues = analyze_java(code_snippet)
    except Exception as e:
        logger.error(f"Error in language-specific analysis: {str(e)}")
        language_specific_issues = [f"Error analyzing code: {str(e)}"]
    
    # Classify issues into syntax errors and logic errors
    for issue in language_specific_issues:
        if "syntax" in issue.lower() or "missing" in issue.lower():
            syntax_errors.append(issue)
        else:
            logic_errors.append(issue)
    
    try:
        # Basic code analysis using CodeBERT
        inputs = tokenizer(code_snippet, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            prediction_score = torch.softmax(logits, dim=1)[0][1].item()  # Probability of "good code"
    except Exception as e:
        logger.error(f"Error in model prediction: {str(e)}")
        prediction_score = 0.5  # Neutral score in case of error
    
    # Additional heuristic analysis
    feedback = []
    issues_found = 0
    
    # Check for common issues in any language
    if "import" not in code_snippet and len(code_snippet) > 100 and language.lower() == "python":
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
    if code_snippet.count('{') != code_snippet.count('}') and language.lower() in ["javascript", "js", "java", "c", "cpp"]:
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
        "logic_errors": logic_errors
    }
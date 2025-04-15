from typing import Dict, Any, List, Optional
import logging
import re
import ast

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyBugHunt:
    """Class that mimics the pybughunt library functionality for code analysis"""
    
    def __init__(self):
        self.detector = CodeErrorDetector()
        
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze Python code for errors and issues"""
        return self.detector.analyze(code)
        
    def get_fix_suggestions(self, code: str, analysis_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate fix suggestions for detected issues"""
        return self.detector.fix_suggestions(code, analysis_results)


class CodeErrorDetector:
    """Implements Python code error detection logic"""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code for syntax and semantic issues
        
        Args:
            code (str): Python code to analyze
            
        Returns:
            dict: Analysis results containing errors and issues
        """
        if not code.strip():
            return {
                "syntax_errors": ["No code provided for analysis."],
                "logic_errors": [],
                "code_quality_issues": [],
                "prediction": 0.0
            }
        
        syntax_errors = []
        logic_errors = []
        code_quality_issues = []
        
        # Check for syntax errors
        try:
            ast.parse(code)
        except SyntaxError as e:
            syntax_errors.append(f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}")
            return {
                "syntax_errors": syntax_errors,
                "logic_errors": [],
                "code_quality_issues": [],
                "prediction": 0.2
            }
        
        # Check for potential logic issues
        if "except:" in code and "pass" in code and re.search(r'except\s*:\s*pass', code):
            logic_errors.append("Bare 'except: pass' blocks found. Consider handling exceptions properly.")
        
        if re.search(r'while\s+True:', code) and not re.search(r'break', code):
            logic_errors.append("Potential infinite loop: 'while True' without a 'break' statement.")
        
        # Check for potential bugs
        if re.search(r'if\s+[^=!<>]+=[^=]+:', code):  # Single = in if statement
            logic_errors.append("Potential bug: Using assignment (=) instead of comparison (==) in conditional statement.")
        
        if re.search(r'return\s+[^:]+\s*if\s+.+\s+else', code) and not re.search(r'return\s+[^:]+\s+if\s+.+\s+else\s+[^:]+', code):
            logic_errors.append("Potential missing return value in ternary expression.")
        
        # Code quality issues
        if re.search(r'print\([^)]*\)', code) and not re.search(r'print\([\'"]', code):
            code_quality_issues.append("Print statements without descriptive strings may make debugging difficult.")
        
        if re.search(r'\b(str|list|dict|set|int|float|bool|tuple|type)\s*=', code):
            code_quality_issues.append("Overwriting built-in type names (str, list, etc.) can lead to unexpected behavior.")
        
        # Check for unused variables
        variable_definitions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code)
        for var in variable_definitions:
            if var != '_' and code.count(var) == 1:
                code_quality_issues.append(f"Variable '{var}' is defined but never used.")
        
        # Calculate a prediction score based on issues found
        total_issues = len(syntax_errors) + len(logic_errors) + len(code_quality_issues)
        base_score = 0.9  # Start with a high score
        deduction_per_issue = 0.1
        prediction_score = max(0.1, min(0.9, base_score - (total_issues * deduction_per_issue)))
        
        return {
            "syntax_errors": syntax_errors,
            "logic_errors": logic_errors,
            "code_quality_issues": code_quality_issues,
            "prediction": prediction_score
        }
    
    def fix_suggestions(self, code: str, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate suggestions to fix the detected issues
        
        Args:
            code (str): Original code
            results (dict): Analysis results
            
        Returns:
            dict: Suggestions for fixing each type of issue
        """
        suggestions = {
            "syntax_fixes": [],
            "logic_fixes": [],
            "quality_fixes": []
        }
        
        # Generate syntax error fixes
        for error in results.get("syntax_errors", []):
            if "syntax error" in error.lower():
                if "EOF" in error:
                    suggestions["syntax_fixes"].append("Check for unclosed parentheses, brackets, or quotes.")
                elif "indent" in error.lower():
                    suggestions["syntax_fixes"].append("Fix indentation to match the structure of your code.")
                else:
                    suggestions["syntax_fixes"].append(f"Fix the syntax error: {error}")
        
        # Generate logic error fixes
        for error in results.get("logic_errors", []):
            if "bare 'except: pass'" in error.lower():
                suggestions["logic_fixes"].append("Replace `except: pass` with specific exception handling, e.g. `except Exception as e: logger.error(str(e))`")
            elif "infinite loop" in error.lower():
                suggestions["logic_fixes"].append("Add a break condition to your while loop or use a terminating condition in the while statement.")
            elif "assignment (=) instead of comparison" in error.lower():
                suggestions["logic_fixes"].append("Replace assignment operator (=) with comparison operator (==) in conditional statements.")
        
        # Generate quality issue fixes
        for issue in results.get("code_quality_issues", []):
            if "print statements without descriptive strings" in issue.lower():
                suggestions["quality_fixes"].append("Add descriptive text to print statements, e.g. `print(f\"Value: {value}\")`")
            elif "overwriting built-in type names" in issue.lower():
                suggestions["quality_fixes"].append("Rename variables that shadow built-in types (don't use variable names like list, dict, str).")
            elif "defined but never used" in issue.lower():
                var_name = re.search(r"'([^']+)'", issue)
                if var_name:
                    suggestions["quality_fixes"].append(f"Remove unused variable '{var_name.group(1)}' or use it in your code.")
        
        return suggestions


def analyze_user_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python code using PyBugHunt
    
    Args:
        code (str): Python code to analyze
        
    Returns:
        dict: Analysis results with suggestions
    """
    try:
        # Create PyBugHunt instance
        bug_hunter = PyBugHunt()
        
        # Analyze the code
        results = bug_hunter.analyze(code)
        
        # Generate fix suggestions
        suggestions = bug_hunter.get_fix_suggestions(code, results)
        
        # Combine results
        return {
            "syntax_errors": results.get("syntax_errors", []),
            "logic_errors": results.get("logic_errors", []),
            "code_quality_issues": results.get("code_quality_issues", []),
            "prediction": results.get("prediction", 0.5),
            "fix_suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return {
            "syntax_errors": [f"Analysis error: {str(e)}"],
            "logic_errors": [],
            "code_quality_issues": [],
            "prediction": 0.0,
            "fix_suggestions": {"syntax_fixes": [], "logic_fixes": [], "quality_fixes": []}
        }
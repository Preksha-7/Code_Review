# backend/app/ai/pybughunt_integration.py
from typing import Dict, Any, List, Optional
import logging
import pybughunt  # Import the actual PyBugHunt library
from pybughunt import CodeErrorDetector  # Import the analyzer component

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_user_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python code using PyBugHunt
    
    Args:
        code (str): Python code to analyze
        
    Returns:
        dict: Analysis results with suggestions
    """
    try:
        # Create analyzer instance
        analyzer = CodeErrorDetector()
        
        # Analyze the code
        results = analyzer.analyze(code)
        
        # Get fix suggestions
        suggestions = analyzer.fix_suggestions(code, results)
        
        # Format the response to match expected structure
        return {
            "syntax_errors": results.get("syntax_errors", []),
            "logic_errors": results.get("logic_errors", []),
            "code_quality_issues": results.get("code_quality_issues", []),
            "prediction": results.get("quality_score", 0.5),
            "fix_suggestions": {
                "syntax_fixes": suggestions.get("syntax_fixes", []),
                "logic_fixes": suggestions.get("logic_fixes", []),
                "quality_fixes": suggestions.get("quality_fixes", [])
            }
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
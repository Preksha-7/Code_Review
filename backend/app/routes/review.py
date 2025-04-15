from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from typing import Optional, List
from app.ai.pybughunt_integration import analyze_user_code
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze")
async def review_code(data: dict = Body(...)):
    """
    Analyze the submitted code snippet using PyBugHunt for Python code
    
    Args:
        data (dict): A dictionary containing the code snippet and language
    
    Returns:
        dict: Code analysis results
    """
    try:
        code_snippet = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code_snippet:
            raise HTTPException(status_code=400, detail="No code snippet provided")
        
        # Only analyze Python code
        if language.lower() != 'python':
            return {
                "prediction": 0.0,
                "overall_feedback": "Unsupported language. Currently only Python is supported.",
                "detailed_feedback": ["This tool currently only supports Python code analysis."],
                "issues_count": 1,
                "syntax_errors": [],
                "logic_errors": []
            }
        
        # Analyze using PyBugHunt
        analysis_result = analyze_user_code(code_snippet)
        
        # Format response
        total_issues = len(analysis_result.get('syntax_errors', [])) + \
                       len(analysis_result.get('logic_errors', [])) + \
                       len(analysis_result.get('code_quality_issues', []))
        
        # Generate overall feedback based on issues found
        if analysis_result.get('syntax_errors', []):
            overall = "Syntax errors detected. Fix these issues before proceeding."
        elif analysis_result.get('prediction', 0) < 0.4 or total_issues > 2:
            overall = "Significant issues detected. Review recommended."
        elif analysis_result.get('prediction', 0) < 0.7 or total_issues > 0:
            overall = "Minor issues found. Consider the suggestions below."
        else:
            overall = "Code looks good! No major issues detected."
        
        # Combine all feedback
        detailed_feedback = []
        detailed_feedback.extend(analysis_result.get('syntax_errors', []))
        detailed_feedback.extend(analysis_result.get('logic_errors', []))
        detailed_feedback.extend(analysis_result.get('code_quality_issues', []))
        
        # Add fix suggestions to feedback if available
        fix_suggestions = analysis_result.get('fix_suggestions', {})
        for fix_type, fixes in fix_suggestions.items():
            detailed_feedback.extend(fixes)
        
        if not detailed_feedback:
            detailed_feedback.append("No specific issues detected.")
        
        return {
            "prediction": analysis_result.get('prediction', 0.5),
            "overall_feedback": overall,
            "detailed_feedback": detailed_feedback,
            "issues_count": total_issues,
            "syntax_errors": analysis_result.get('syntax_errors', []),
            "logic_errors": analysis_result.get('logic_errors', []),
            "fix_suggestions": analysis_result.get('fix_suggestions', {})
        }
    
    except Exception as e:
        logger.error(f"Code analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages():
    """
    Returns a list of supported programming languages for code analysis
    
    Returns:
        dict: List of supported languages with their identifiers
    """
    # Currently only supporting Python
    supported_languages = [
        {"id": "python", "name": "Python", "description": "Python 3.x"},
    ]
    
    return {"languages": supported_languages}

@router.post("/feedback")
async def submit_feedback(data: dict = Body(...)):
    """
    Submit feedback on code analysis to improve the analysis
    
    Args:
        data (dict): A dictionary containing feedback data
        
    Returns:
        dict: Confirmation message
    """
    try:
        code_snippet = data.get('code', '')
        user_score = data.get('user_score', 0)
        model_score = data.get('model_score', 0)
        issues = data.get('issues', [])
        missed_issues = data.get('missed_issues', [])
        false_positives = data.get('false_positives', [])
        
        logger.info(f"Received feedback: user_score={user_score}, model_score={model_score}")
        
        return {"status": "success", "message": "Feedback received successfully"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")
# backend/app/routes/review.py
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
                "logic_errors": [],
                "code_quality_issues": []
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
        
        # Combine all feedback into detailed_feedback
        detailed_feedback = []
        detailed_feedback.extend(analysis_result.get('syntax_errors', []))
        detailed_feedback.extend(analysis_result.get('logic_errors', []))
        detailed_feedback.extend(analysis_result.get('code_quality_issues', []))
        
        if not detailed_feedback:
            detailed_feedback.append("No specific issues detected.")
        
        return {
            "prediction": analysis_result.get('prediction', 0.5),
            "overall_feedback": overall,
            "detailed_feedback": detailed_feedback,
            "issues_count": total_issues,
            "syntax_errors": analysis_result.get('syntax_errors', []),
            "logic_errors": analysis_result.get('logic_errors', []),
            "code_quality_issues": analysis_result.get('code_quality_issues', []),
            "fix_suggestions": analysis_result.get('fix_suggestions', {})
        }
    
    except Exception as e:
        logger.error(f"Code analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")
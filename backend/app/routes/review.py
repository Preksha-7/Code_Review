from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from typing import Optional, List
from app.ai.codebert_analyzer import analyze_code
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze")
async def review_code(data: dict = Body(...)):
    """
    Analyze the submitted code snippet using CodeBERT and ML models
    
    Args:
        data (dict): A dictionary containing the code snippet and language
    
    Returns:
        dict: Code analysis results
    """
    try:
        code_snippet = data.get('code', '')
        language = data.get('language', 'python')  # Default to python if not specified
        auto_detect = data.get('auto_detect', True)  # Default to auto-detecting language
        
        if not code_snippet:
            raise HTTPException(status_code=400, detail="No code snippet provided")
        
        analysis_result = analyze_code(
            code_snippet=code_snippet, 
            language=language,
            detect_lang=auto_detect
        )
        
        # Log detection of language mismatches for monitoring
        if analysis_result.get('detected_language') and analysis_result.get('detected_language') != language:
            logger.info(f"Language mismatch: Submitted as {language}, detected as {analysis_result['detected_language']}")
        
        return analysis_result
    
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
    supported_languages = [
        {"id": "python", "name": "Python", "description": "Python 3.x"},
        {"id": "javascript", "name": "JavaScript", "description": "ES6+ JavaScript"},
        {"id": "java", "name": "Java", "description": "Java 8+"},
        {"id": "cpp", "name": "C++", "description": "C++11 and later"},
        {"id": "csharp", "name": "C#", "description": "C# (.NET)"},
    ]
    
    return {"languages": supported_languages}

@router.post("/feedback")
async def submit_feedback(data: dict = Body(...)):
    """
    Submit feedback on code analysis to improve the ML models
    
    Args:
        data (dict): A dictionary containing feedback data
        
    Returns:
        dict: Confirmation message
    """
    try:
        code_snippet = data.get('code', '')
        language = data.get('language', '')
        detected_language = data.get('detected_language', '')
        user_score = data.get('user_score', 0)  # User's rating of the code quality (0-100)
        model_score = data.get('model_score', 0)  # Model's predicted score
        issues = data.get('issues', [])  # Issues identified
        missed_issues = data.get('missed_issues', [])  # Issues missed by the analyzer
        false_positives = data.get('false_positives', [])  # False positive issues
        
        # Here you would store this feedback for later model training
        # For now we just log it
        logger.info(f"Received feedback: lang={language}, user_score={user_score}, model_score={model_score}")
        
        # In a production system, you would:
        # 1. Store this feedback in a database
        # 2. Periodically retrain models using collected feedback
        
        return {"status": "success", "message": "Feedback received successfully"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")

@router.post("/train")
async def trigger_training(data: dict = Body(...)):
    """
    Admin endpoint to trigger ML model training based on collected feedback
    
    Args:
        data (dict): Training configuration options
        
    Returns:
        dict: Training status
    """
    # This would be protected with admin authentication in production
    try:
        train_language_model = data.get('train_language_model', False)
        train_quality_model = data.get('train_quality_model', False)
        
        if train_language_model:
            # Code to trigger language model training from collected data
            logger.info("Language detection model training triggered")
            
        if train_quality_model:
            # Code to trigger quality model training from collected data
            logger.info("Code quality model training triggered")
            
        return {
            "status": "success", 
            "message": "Training jobs initiated"
        }
        
    except Exception as e:
        logger.error(f"Error triggering training: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate training")
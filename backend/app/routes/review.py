from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
import requests
from app.config import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL
from app.database import save_user
from app.ai.codebert_analyzer import analyze_code
from typing import Optional

router = APIRouter()

@router.post("/analyze")
async def review_code(data: dict = Body(...)):
    """
    Analyze the submitted code snippet using CodeBERT
    
    Args:
        data (dict): A dictionary containing the code snippet and language
    
    Returns:
        dict: Code analysis results
    """
    try:
        code_snippet = data.get('code', '')
        language = data.get('language', 'python')  # Default to python if not specified
        
        if not code_snippet:
            raise HTTPException(status_code=400, detail="No code snippet provided")
        
        analysis_result = analyze_code(code_snippet, language)
        return analysis_result
    
    except Exception as e:
        print(f"Code analysis error: {str(e)}")
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
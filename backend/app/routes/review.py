from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.codebert_analyzer import analyze_code  # Fixed import

router = APIRouter()

class CodeReviewRequest(BaseModel):
    code: str

@router.post("/analyze")
async def analyze_code_api(request: CodeReviewRequest):
    """
    Analyzes a given code snippet using CodeBERT AI.
    """
    if not request.code or request.code.strip() == "":
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        analysis = analyze_code(request.code)
        return {"message": "Analysis successful", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

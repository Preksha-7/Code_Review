from fastapi import APIRouter, HTTPException, Depends
from app.database import get_database
from typing import List, Optional
from pydantic import BaseModel
from app.ai.codebert_analyzer import analyze_code as codebert_analyze
import logging
from fastapi.security import OAuth2PasswordBearer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Define Pydantic models for validation
class Review(BaseModel):
    user_id: str
    code_snippet: str
    feedback: str
    rating: int

class CodeAnalysisRequest(BaseModel):
    code: str

class AnalysisResponse(BaseModel):
    prediction: float
    overall_feedback: str
    detailed_feedback: List[str]
    issues_count: int

# Create a new review
@router.post("/")
async def create_review(review: Review):
    try:
        db = await get_database()
        review_dict = review.dict()
        result = await db.reviews.insert_one(review_dict)
        return {"message": "Review added successfully", "review_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding review: {str(e)}")

# Get all reviews
@router.get("/", response_model=List[Review])
async def get_reviews():
    try:
        db = await get_database()
        reviews_cursor = db.reviews.find()
        reviews = await reviews_cursor.to_list(length=100)  # Adjust as needed
        return reviews
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")

# Get a specific review by user_id
@router.get("/{user_id}", response_model=List[Review])
async def get_reviews_by_user(user_id: str):
    try:
        db = await get_database()
        reviews_cursor = db.reviews.find({"user_id": user_id})
        reviews = await reviews_cursor.to_list(length=100)  # Adjust as needed
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this user.")
        return reviews
    except Exception as e:
        logger.error(f"Error fetching user reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user reviews: {str(e)}")

# Update an existing review by review_id
@router.put("/{review_id}")
async def update_review(review_id: str, updated_review: Review):
    try:
        from bson.objectid import ObjectId
        db = await get_database()
        result = await db.reviews.update_one(
            {"_id": ObjectId(review_id)}, {"$set": updated_review.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found.")
        return {"message": "Review updated successfully"}
    except Exception as e:
        logger.error(f"Error updating review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")

# Delete a review by review_id
@router.delete("/{review_id}")
async def delete_review(review_id: str):
    try:
        from bson.objectid import ObjectId
        db = await get_database()
        result = await db.reviews.delete_one({"_id": ObjectId(review_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found.")
        return {"message": "Review deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting review: {str(e)}")

# Add code analysis endpoint with improved response
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logger.info("Analyzing code snippet...")
        if not request.code or len(request.code.strip()) == 0:
            return {
                "prediction": 0.0,
                "overall_feedback": "No code provided to analyze.",
                "detailed_feedback": ["Please provide a code snippet for analysis."],
                "issues_count": 1
            }
            
        result = codebert_analyze(request.code)
        logger.info(f"Analysis complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")
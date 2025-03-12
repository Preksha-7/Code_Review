from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI  # Ensure this is in your config
from typing import List
from pydantic import BaseModel

router = APIRouter()

# ✅ Connect to MongoDB asynchronously
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("your_database_name")  # Replace with actual DB name
reviews_collection = db.reviews


# ✅ Define Pydantic model for validation
class Review(BaseModel):
    user_id: str
    code_snippet: str
    feedback: str
    rating: int


# ✅ Create a new review
@router.post("/")
async def create_review(review: Review):
    try:
        review_dict = review.dict()
        result = await reviews_collection.insert_one(review_dict)
        return {"message": "Review added successfully", "review_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding review: {str(e)}")


# ✅ Get all reviews
@router.get("/", response_model=List[Review])
async def get_reviews():
    try:
        reviews_cursor = reviews_collection.find()
        reviews = await reviews_cursor.to_list(length=100)  # Adjust as needed
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")


# ✅ Get a specific review by user_id
@router.get("/{user_id}", response_model=List[Review])
async def get_reviews_by_user(user_id: str):
    try:
        reviews_cursor = reviews_collection.find({"user_id": user_id})
        reviews = await reviews_cursor.to_list(length=100)  # Adjust as needed
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this user.")
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user reviews: {str(e)}")


# ✅ Update an existing review by user_id
@router.put("/{user_id}")
async def update_review(user_id: str, updated_review: Review):
    try:
        result = await reviews_collection.update_one(
            {"user_id": user_id}, {"$set": updated_review.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found.")
        return {"message": "Review updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")


# ✅ Delete a review by user_id
@router.delete("/{user_id}")
async def delete_review(user_id: str):
    try:
        result = await reviews_collection.delete_one({"user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found.")
        return {"message": "Review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting review: {str(e)}")

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME, USE_LOCAL_DB

# Global client variable - connection is only established when needed
_client = None

async def get_database():
    """Get or create the database connection"""
    global _client
    if _client is None:
        # Different connection options for local vs. Atlas
        if USE_LOCAL_DB:
            _client = AsyncIOMotorClient(MONGO_URI)
        else:
            _client = AsyncIOMotorClient(
                MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True
            )
    return _client[DATABASE_NAME]

async def get_user(email: str):
    """Get a user by email"""
    db = await get_database()
    return await db.users.find_one({"email": email})

async def get_user_by_sub(sub: str):
    """Get a user by Auth0 sub ID"""
    db = await get_database()
    return await db.users.find_one({"sub": sub})

async def save_user(user_data: dict):
    """Save or update a user"""
    db = await get_database()
    existing_user = await db.users.find_one({"sub": user_data.get("sub")})
    if not existing_user:
        result = await db.users.insert_one(user_data)
        return {"inserted_id": str(result.inserted_id), "is_new": True}
    else:
        result = await db.users.update_one({"sub": user_data.get("sub")}, {"$set": user_data})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count, "is_new": False}
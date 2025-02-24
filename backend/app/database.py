from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DATABASE_NAME

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True
)
db = client[DATABASE_NAME]
users_collection = db["users"]

async def get_user(email: str):
    return await users_collection.find_one({"email": email})

async def save_user(user_data: dict):
    existing_user = await users_collection.find_one({"sub": user_data.get("sub")})
    if not existing_user:
        await users_collection.insert_one(user_data)
    else:
        await users_collection.update_one({"sub": user_data.get("sub")}, {"$set": user_data})

import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL") or "http://localhost:8000/auth/callback"

# Database configuration
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not DATABASE_NAME:
    print("❌ ERROR: DATABASE_NAME not set in .env")
    exit(1)

# Choose between local and Atlas MongoDB
if USE_LOCAL_DB:
    MONGO_URI = "mongodb://localhost:27017/"
    print("✅ Using local MongoDB. Database:", DATABASE_NAME)
else:
    import urllib.parse
    # MongoDB Atlas credentials
    USERNAME = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME"))
    PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
    CLUSTER_URL = os.getenv("MONGO_CLUSTER")
    
    if not all([USERNAME, PASSWORD, CLUSTER_URL]):
        print("❌ ERROR: MongoDB Atlas credentials not properly set in .env")
        exit(1)
    
    # Construct the connection URI properly using environment variables
    MONGO_URI = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{DATABASE_NAME}?retryWrites=true&w=majority"
    print("✅ Using MongoDB Atlas. Database:", DATABASE_NAME)
import os
import urllib.parse
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Fetch URI components
USERNAME = urllib.parse.quote_plus("prekshaupadhyay03")
PASSWORD = urllib.parse.quote_plus("Seven@07")  # Encodes '@' correctly
CLUSTER_URL = "cluster0.qwtsl.mongodb.net"
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Construct the encoded MongoDB URI
MONGO_URI = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/?retryWrites=true&w=majority&appName=Cluster0"

# Ensure database name is set
if not DATABASE_NAME:
    print("❌ ERROR: DATABASE_NAME not set in .env")
    exit(1)

# Establish MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Check connection
print("✅ Connected to MongoDB Atlas. Database:", db.name)

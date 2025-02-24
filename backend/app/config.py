import os
import urllib.parse
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env located in the same directory as this file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
# Use the value from .env for callback URL
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL") or "http://localhost:8000/auth/callback"

# Hardcoded MongoDB credentials (ideally these should be in your .env)
USERNAME = urllib.parse.quote_plus("prekshaupadhyay03")
PASSWORD = urllib.parse.quote_plus("Seven@07")  # Encodes '@' correctly
CLUSTER_URL = "cluster0.qwtsl.mongodb.net"
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not DATABASE_NAME:
    print("❌ ERROR: DATABASE_NAME not set in .env")
    exit(1)

# Construct the connection URI without any insecure flags in the URI itself.
MONGO_URI = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/?retryWrites=true&w=majority&appName=Cluster0"

# Establish MongoDB connection with insecure TLS options for testing only.
# WARNING: Do not use tlsAllowInvalidCertificates=True and tlsAllowInvalidHostnames=True in production!
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True
)
db = client[DATABASE_NAME]

print("✅ Connected to MongoDB Atlas. Database:", db.name)

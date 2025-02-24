from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
import requests
from app.config import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL, db  # Fixed import
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, review  # Fixed import

app = FastAPI(title="AI Code Review Platform")

# Set up CORS for your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from the auth and review modules
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(review.router, prefix="/review", tags=["Review"])

# OAuth2 scheme (if used elsewhere in your app)
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token"
)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Code Review Platform"}

# Endpoint to generate Auth0 authorization URL
@app.get("/auth/github")
def github_login():
    return {
        "auth_url": (
            f"https://{AUTH0_DOMAIN}/authorize"
            f"?response_type=code"
            f"&client_id={AUTH0_CLIENT_ID}"
            f"&redirect_uri={AUTH0_CALLBACK_URL}"
            f"&scope=openid profile email"
        )
    }

# Callback endpoint: exchange code for token, get user info, and store/update essential user data in MongoDB.
@app.get("/auth/callback")
def github_callback(code: str):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_CALLBACK_URL,
    }
    
    response = requests.post(token_url, json=payload)
    if response.status_code != 200:
        error_details = response.text
        print("Error retrieving token:", response.status_code, error_details)
        raise HTTPException(status_code=400, detail=f"Failed to retrieve access token: {error_details}")
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found in the response.")
    
    user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")
    
    user_info = user_response.json()
    
    # Store/Update user data in MongoDB
    user_data = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "sub": user_info.get("sub"),
        "picture": user_info.get("picture"),
    }
    
    try:
        users_collection = db.users
        existing_user = users_collection.find_one({"sub": user_data["sub"]})
        if existing_user is None:
            users_collection.insert_one(user_data)
            print("Inserted new user:", user_data["email"])
        else:
            users_collection.update_one({"sub": user_data["sub"]}, {"$set": user_data})
            print("Updated existing user:", user_data["email"])
    except Exception as e:
        print("Error storing user data in MongoDB:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error while storing user data")
    
    return {"message": "Login successful", "user": user_info}

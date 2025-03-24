from fastapi import FastAPI, HTTPException, Response
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from fastapi import APIRouter

import requests
from app.config import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL
from app.database import save_user
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, review

app = FastAPI(title="AI Code Review Platform")

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


router = APIRouter()

@router.get("/github")
async def github_login():
    auth_url = (
        f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
    )
    return RedirectResponse(url=auth_url)

# Endpoint to generate Auth0 authorization URL
@app.get("/auth/callback")
async def github_callback(code: str):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_CALLBACK_URL,
    }
    
    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token not found in the response.")
        
        user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()  # Raise exception for HTTP errors
        
        user_info = user_response.json()
        
        # Store/Update user data in MongoDB using async function
        user_data = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "sub": user_info.get("sub"),
            "picture": user_info.get("picture"),
        }
        
        # Use the async save_user function from database.py
        result = await save_user(user_data)
        if result.get("is_new"):
            print("Inserted new user:", user_data["email"])
        else:
            print("Updated existing user:", user_data["email"])
        
        # Set a cookie with user information (optional but useful)
        frontend_url = "http://localhost:3000"
        redirect_url = f"{frontend_url}?auth=success&token={access_token}"
        
        # Return a redirect response to the frontend
        return RedirectResponse(url=redirect_url)
        
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        print("Error in OAuth flow:", error_details)
        raise HTTPException(status_code=500, detail=f"OAuth flow error: {error_details}")
    except Exception as e:
        print("Unexpected error during authentication:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error during authentication")
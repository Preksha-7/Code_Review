from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
import requests
from app.config import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL
from app.database import save_user
from app.ai.codebert_analyzer import analyze_code

router = APIRouter()

# Route to initiate GitHub OAuth flow
@router.get("/github")
async def github_login():
    auth_url = (
        f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
    )
    return {"auth_url": auth_url}  # JSON response for frontend logic compatibility

# OAuth callback route
@router.get("/callback")
async def github_callback(code: str, request: Request):
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
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token not found in the response.")
        
        user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()

        user_info = user_response.json()

        user_data = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "sub": user_info.get("sub"),
            "picture": user_info.get("picture"),
        }

        result = await save_user(user_data)
        action = "Inserted new user" if result.get("is_new") else "Updated existing user"
        print(f"{action}: {user_data['email']}")

        # Encode token and user data in the URL
        from urllib.parse import urlencode
        frontend_url = "http://localhost:3000"
        redirect_params = urlencode({
            "auth": "success", 
            "token": access_token,
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "picture": user_data.get("picture", "")
        })
        
        # Return a redirect response to the frontend
        return RedirectResponse(url=f"{frontend_url}?{redirect_params}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"OAuth flow error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Unexpected response structure: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during authentication")

# Route to fetch user info
@router.get("/userinfo")
async def get_user_info(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    
    token = authorization.split(" ")[1]
    try:
        user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user info: {str(e)}")
    
    
@router.post("/analyze")
async def review_code(code: dict = Body(...)):
    """
    Analyze the submitted code snippet using CodeBERT
    
    Args:
        code (dict): A dictionary containing the code snippet
    
    Returns:
        dict: Code analysis results
    """
    try:
        code_snippet = code.get('code', '')
        
        if not code_snippet:
            raise HTTPException(status_code=400, detail="No code snippet provided")
        
        analysis_result = analyze_code(code_snippet)
        return analysis_result
    
    except Exception as e:
        print(f"Code analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")
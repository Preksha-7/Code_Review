from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.get("/github-info")
async def github_auth_info():
    # This endpoint is optional and can be used for debugging GitHub credentials.
    return JSONResponse(content={"client_id": os.getenv("GITHUB_CLIENT_ID"), "message": "GitHub info endpoint"})

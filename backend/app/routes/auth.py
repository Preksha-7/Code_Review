from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@router.get("/github")
async def github_auth():
    return JSONResponse(content={"client_id": GITHUB_CLIENT_ID, "message": "Use this to authenticate with GitHub"})

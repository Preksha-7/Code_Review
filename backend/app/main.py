from fastapi import FastAPI
from app.routes import auth, review

app = FastAPI(title="AI Code Review Platform")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(review.router, prefix="/review", tags=["Review"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Code Review Platform"}


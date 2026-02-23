from fastapi import APIRouter
from app.api.routes import posts, auth, user

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(user.router)
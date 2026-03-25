from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router
from .categories import router as categories_router
from .tags import router as tags_router
from .comments import router as comments_router
from .media import router as media_router
from .admin import router as admin_router
from .follows import router as follows_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(posts_router)
api_router.include_router(categories_router)
api_router.include_router(tags_router)
api_router.include_router(comments_router)
api_router.include_router(media_router)
api_router.include_router(admin_router)
api_router.include_router(follows_router)

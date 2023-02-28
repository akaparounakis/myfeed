from fastapi import APIRouter

from app.api import users, articles

router = APIRouter(prefix='/api/v1')
router.include_router(users.router, prefix='/users')
router.include_router(articles.router, prefix='/articles')

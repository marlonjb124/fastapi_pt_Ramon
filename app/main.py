from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.services import sessionmanager
from app.routers.user import router as router_users
from app.routers.auth import router as router_auth
from app.routers.posts import router as router_posts
@asynccontextmanager
async def lifespan(app: FastAPI):
    sessionmanager.init(settings.DATABASE_URL)
    yield
    
    await sessionmanager.close()


myapp = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)


myapp.include_router(router_users, prefix=settings.API_V1_STR)
myapp.include_router(router_auth, prefix=settings.API_V1_STR)
myapp.include_router(router_posts, prefix=settings.API_V1_STR)
    

@myapp.get("/health")
async def health_check():
    return {"status": "healthy"}
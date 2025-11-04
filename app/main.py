from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from app.core.config import settings
from app.db.services import sessionmanager
from app.routers.user import router as router_users
from app.routers.auth import router as router_auth
from app.routers.posts import router as router_posts
from app.routers.tags import router as router_tags
from app.routers.admin import router as router_admin
from app.routers.premium import router as router_premium
import time


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
myapp.include_router(router_tags, prefix=settings.API_V1_STR)
myapp.include_router(router_admin, prefix=settings.API_V1_STR)
myapp.include_router(router_premium, prefix=settings.API_V1_STR)
    
@myapp.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print("process_time",process_time)
    return response
@myapp.get("/health")
async def health_check():
    return {"status": "healthy"}
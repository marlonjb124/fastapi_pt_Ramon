from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.services import sessionmanager
from app.routers.user import router as router_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    sessionmanager.init(settings.DATABASE_URL)
    yield
    
    await sessionmanager.close()

# Create FastAPI application
myapp = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Include routers
myapp.include_router(router_users, prefix=settings.API_V1_STR)
    

@myapp.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
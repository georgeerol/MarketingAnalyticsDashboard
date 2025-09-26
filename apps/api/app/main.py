"""
FastAPI application factory and main entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.database import init_db
from app.api.v1 import api_router

# Setup logging
setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Google Meridian Media Mix Modeling Dashboard API",
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok", 
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.APP_NAME,
        "description": "Google Meridian Media Mix Modeling Dashboard",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        await init_db()
        print(f"✅ Database initialized successfully")
        print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
        print(f"📚 API docs available at: /docs")
        print(f"🔗 API v1 prefix: {settings.API_V1_PREFIX}")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't fail startup, just log the error
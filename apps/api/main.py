from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routes.auth import router as auth_router
from database import init_db

settings = get_settings()
app: FastAPI = FastAPI(
    title="MMM Dashboard API",
    description="Google Meridian Media Mix Modeling Dashboard API",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MMM Dashboard API"}


@app.get("/")
async def root():
    return {
        "message": "MMM Dashboard API",
        "description": "Google Meridian Media Mix Modeling Dashboard",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Don't fail startup, just log the error

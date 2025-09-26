from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import create_tables
from routes.auth import router as auth_router

settings = get_settings()
app: FastAPI = FastAPI(
    title="Marketing Analytics Dashboard API",
    description="API for user authentication and marketing analytics dashboard",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Marketing Analytics API"}

@app.get("/")
async def root():
    return {
        "message": "Marketing Analytics Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api-info")
async def api_info():
    return {
        "name": "Marketing Analytics Dashboard API",
        "description": "User authentication and marketing analytics with Google Meridian model integration",
        "features": [
            "User registration and authentication",
            "JWT token-based authorization",
            "User profile management",
            "Google Meridian model integration (planned)",
            "Interactive data visualizations (planned)"
        ],
        "endpoints": {
            "auth": "/auth/* (register, login, me, verify-token)",
            "health": "/health",
            "info": "/api-info"
        }
    }

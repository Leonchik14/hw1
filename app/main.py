"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="MLOps Homework 1 API",
    description="API for training, managing, and using ML models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["api"])

@app.get("/")
async def root():
    """
    Root endpoint - redirects to API documentation.
    
    Returns:
        Information about the API and links to documentation
    """
    return {
        "message": "MLOps Homework 1 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_base": "/api/v1",
        "endpoints": {
            "health": "/api/v1/health",
            "models": "/api/v1/models",
            "datasets": "/api/v1/datasets"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting MLOps API service")
    logger.info(f"API will be available at http://{settings.api_host}:{settings.api_port}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down MLOps API service")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )






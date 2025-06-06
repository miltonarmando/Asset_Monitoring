import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable
import traceback

from .database import engine, SessionLocal, init_db
from .models import init_models
from .api.api_v1.api import api_router
from .core.redis import init_redis
from .core.config import settings
from .tasks.collector import SNMPCollector
from .tasks.alert_evaluator import AlertEvaluator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events"""
    # Initialize database and models
    init_models()
    init_db()
    logger.info("Initialized database and models")
    
    # Initialize Redis
    await init_redis()
    logger.info("Initialized Redis")
    
    # Start SNMP collector
    collector = SNMPCollector()
    asyncio.create_task(collector.start(interval=300))  # 5-minute interval
    logger.info("Started SNMP collector")

    # Start AlertEvaluator
    alert_evaluator = AlertEvaluator(interval=60)  # check every 60 seconds
    asyncio.create_task(alert_evaluator.start())
    logger.info("Started AlertEvaluator")
    
    yield  # The application runs here
    
    # Clean up resources on shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Network Switch Monitoring API",
    description="API for monitoring Cisco and Huawei network devices",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS: permitir frontend local e outros ambientes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create static files directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that logs all unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Query params: {request.query_params}\n"
        f"Client: {request.client}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create static files directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint to check if the API is running"""
    return {
        "message": "Network Switch Monitoring API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    # Add database health check
    db = SessionLocal()
    try:
        # Simple query to check database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )
    finally:
        db.close()
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        workers=int(os.getenv("WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
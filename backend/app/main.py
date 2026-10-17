"""
PlanWise AI - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db
from app.routers import tasks, assistant, schedule, settings as settings_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("PlanWise AI starting up...")
    init_db()
    logger.info(f"Database initialized. AI available: {settings.ai_available}")
    if settings.ai_available:
        logger.info(f"AI provider: {settings.active_ai_provider}")
    else:
        logger.info("No AI configured — using rule-based fallback")
    yield
    logger.info("PlanWise AI shutting down.")


app = FastAPI(
    title="PlanWise AI",
    description=(
        "A conversational AI task manager and daily scheduler. "
        "This is a simulated Alexa+ experience built for the Amazon Developer Hackathon."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
cors_origins = settings.cors_origins_list
allow_all = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if not allow_all else None,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(tasks.router)
app.include_router(assistant.router)
app.include_router(schedule.router)
app.include_router(settings_router.router)


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "PlanWise AI",
        "version": "1.0.0",
        "ai_available": settings.ai_available,
        "ai_provider": settings.active_ai_provider,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to PlanWise AI API",
        "docs": "/docs",
        "health": "/health",
    }

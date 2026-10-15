import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR
from backend.services.background_removal import get_background_remover
from backend.api.photo import router as photo_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Snap2Print")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Warms up the background model once during server start
    so the first request does not incur cold-start latency.
    """
    logger.info("Snap2Print starting up. Initializing lightweight model...")
    try:
        get_background_remover()
        logger.info("Model pre-loaded and ready for fast CPU inference.")
    except Exception as e:
        logger.warning(f"Model warm-up deferred or failed: {e}. Will initialize on first request.")
    yield
    logger.info("Snap2Print shutting down.")


app = FastAPI(
    title="Snap2Print Studio API",
    description="AI-assisted photo processing tool for small photo studios (Phase 1)",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local dev / desktop usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include photo router
app.include_router(photo_router)

# Mount static frontend
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import create_tables

from services.score_fetcher import run_score_sync

from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn, logging, os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SportsBet AI API", version="2.0.0")

import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)

scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup():
    create_tables()
    logger.info("✅ DB tables ready")
    # Run immediately on boot, then every 5 minutes
    try:
        run_score_sync()
    except Exception as e:
        logger.warning(f"Initial score sync failed (non-fatal): {e}")
    scheduler.add_job(run_score_sync, "interval", minutes=5, id="score_sync",
                      max_instances=1, misfire_grace_time=60)
    scheduler.start()
    logger.info("⏰ Score sync scheduler started (every 5 min)")


@app.on_event("shutdown")
def shutdown():
    if scheduler.running:
        scheduler.shutdown(wait=False)


# ── Routers ───────────────────────────────────────────────────────────────────
# FIX: Wrap each router import in try/except so missing routers don't crash the whole app
def _try_include(module_path: str, prefix: str, tags: list):
    try:
        import importlib
        mod = importlib.import_module(module_path)
        app.include_router(mod.router, prefix=prefix, tags=tags)
        logger.info(f"✅ Router loaded: {prefix}")
    except Exception as e:
        logger.warning(f"⚠️  Router not loaded ({module_path}): {e}")

_try_include("routers.soccer",  "/api/soccer",  ["Soccer"])
_try_include("routers.nba",     "/api/nba",     ["NBA"])
_try_include("routers.nfl",     "/api/nfl",     ["NFL"])
_try_include("routers.tennis",  "/api/tennis",  ["Tennis"])
_try_include("routers.records", "/api/records", ["Records"])


# ── Core endpoints ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "SportsBet AI v2.0", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/sync/scores")
def manual_sync():
    """Trigger a manual score sync."""
    try:
        updated = run_score_sync()
        return {"status": "done", "updated": updated}
    except Exception as e:
        logger.error(f"Manual sync error: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    reload = os.environ.get("ENV") != "production"
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)

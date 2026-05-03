from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import soccer, nba, nfl, tennis, records
from database import create_tables
from services.score_fetcher import run_score_sync
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn, logging

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
    # Run immediately on boot then every 5 minutes
    run_score_sync()
    scheduler.add_job(run_score_sync, "interval", minutes=5, id="score_sync")
    scheduler.start()
    logger.info("⏰ Score sync scheduler started (every 5 min)")

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()

app.include_router(soccer.router,  prefix="/api/soccer",  tags=["Soccer"])
app.include_router(nba.router,     prefix="/api/nba",     tags=["NBA"])
app.include_router(nfl.router,     prefix="/api/nfl",     tags=["NFL"])
app.include_router(tennis.router,  prefix="/api/tennis",  tags=["Tennis"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])

@app.get("/")
def root():
    return {"status": "SportsBet AI v2.0", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/sync/scores")
def manual_sync():
    """Trigger a manual score sync (useful for testing)."""
    updated = run_score_sync()
    return {"status": "done", "updated": updated}

if __name__ == "__main__":
    reload = os.environ.get("ENV") != "production"
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)

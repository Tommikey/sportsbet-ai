"""
Database setup using SQLAlchemy + PostgreSQL.
Falls back to SQLite locally if no DATABASE_URL env var set.
"""
import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, Boolean, JSON, ForeignKey, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./sportsbet.db"  # local fallback
)

# Railway PostgreSQL uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── MODELS ──────────────────────────────────────────────────────────────────

class DailyPrediction(Base):
    """Stores every prediction made each day."""
    __tablename__ = "daily_predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, index=True)
    sport = Column(String(20), index=True)          # soccer / nba / nfl / tennis
    league = Column(String(100))
    home_team = Column(String(100))
    away_team = Column(String(100))
    match_date = Column(String(50))                  # scheduled kickoff
    prediction = Column(String(50))                  # Home Win / Draw / Away Win
    confidence = Column(Float)
    bet_value = Column(String(30))                   # HIGH VALUE / MODERATE / LOW VALUE
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    intel = Column(Text, nullable=True)
    goals_data = Column(JSON, nullable=True)         # over/under + correct score
    source = Column(String(20), default="curated")   # live / curated
    created_at = Column(DateTime, default=datetime.utcnow)

    # Result (filled in later)
    result = relationship("MatchResult", back_populates="prediction", uselist=False)


class MatchResult(Base):
    """Actual match results — filled in after game is played."""
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("daily_predictions.id"), unique=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    actual_result = Column(String(50), nullable=True)   # Home Win / Draw / Away Win
    prediction_correct = Column(Boolean, nullable=True)
    over_25_correct = Column(Boolean, nullable=True)
    btts_correct = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("DailyPrediction", back_populates="result")


class ModelAccuracy(Base):
    """Rolling accuracy tracker per sport."""
    __tablename__ = "model_accuracy"

    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String(20), index=True)
    date = Column(Date, default=date.today)
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy_pct = Column(Float, default=0.0)
    high_value_total = Column(Integer, default=0)
    high_value_correct = Column(Integer, default=0)


def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

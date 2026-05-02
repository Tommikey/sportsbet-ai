"""
Records router — save predictions, log results, view history.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db, DailyPrediction, MatchResult, ModelAccuracy
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, timedelta

router = APIRouter()


# ─── SCHEMAS ─────────────────────────────────────────────────────────────────

class SavePredictionIn(BaseModel):
    sport: str
    league: str
    home_team: str
    away_team: str
    match_date: str
    prediction: str
    confidence: float
    bet_value: str
    home_win_prob: float
    draw_prob: Optional[float] = 0.0
    away_win_prob: float
    intel: Optional[str] = None
    goals_data: Optional[dict] = None
    source: Optional[str] = "curated"

class ResultIn(BaseModel):
    prediction_id: int
    home_score: int
    away_score: int
    notes: Optional[str] = None

class BulkSaveIn(BaseModel):
    predictions: List[SavePredictionIn]


# ─── SAVE PREDICTIONS ────────────────────────────────────────────────────────

@router.post("/save")
def save_prediction(data: SavePredictionIn, db: Session = Depends(get_db)):
    """Save a single prediction to the database."""
    # Check if already saved today for this match
    existing = db.query(DailyPrediction).filter(
        DailyPrediction.date == date.today(),
        DailyPrediction.home_team == data.home_team,
        DailyPrediction.away_team == data.away_team,
        DailyPrediction.sport == data.sport,
    ).first()

    if existing:
        return {"status": "already_saved", "id": existing.id}

    pred = DailyPrediction(**data.dict())
    pred.date = date.today()
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return {"status": "saved", "id": pred.id}


@router.post("/save/bulk")
def save_bulk(data: BulkSaveIn, db: Session = Depends(get_db)):
    """Save all predictions for a sport in one call."""
    saved, skipped = 0, 0
    ids = []
    for p in data.predictions:
        existing = db.query(DailyPrediction).filter(
            DailyPrediction.date == date.today(),
            DailyPrediction.home_team == p.home_team,
            DailyPrediction.away_team == p.away_team,
            DailyPrediction.sport == p.sport,
        ).first()
        if existing:
            skipped += 1
            ids.append(existing.id)
            continue
        pred = DailyPrediction(**p.dict())
        pred.date = date.today()
        db.add(pred)
        db.flush()
        ids.append(pred.id)
        saved += 1
    db.commit()
    return {"status": "ok", "saved": saved, "skipped": skipped, "ids": ids}


# ─── LOG RESULTS ─────────────────────────────────────────────────────────────

@router.post("/result")
def log_result(data: ResultIn, db: Session = Depends(get_db)):
    """Log the actual result for a prediction."""
    pred = db.query(DailyPrediction).filter(DailyPrediction.id == data.prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    h, a = data.home_score, data.away_score
    if h > a:
        actual = "Home Win"
    elif a > h:
        actual = "Away Win"
    else:
        actual = "Draw"

    correct = (actual == pred.prediction)
    total = h + a
    over25 = total > 2.5
    btts = h >= 1 and a >= 1

    # Check our over/under prediction
    over25_pred = None
    btts_pred = None
    if pred.goals_data and pred.goals_data.get("markets"):
        m = pred.goals_data["markets"]
        over25_pred = m.get("over_2_5", {}).get("recommendation") == "YES"
        btts_pred = m.get("btts", {}).get("recommendation") == "YES"

    result = MatchResult(
        prediction_id=pred.id,
        home_score=h,
        away_score=a,
        actual_result=actual,
        prediction_correct=correct,
        over_25_correct=(over25_pred is not None and over25_pred == over25),
        btts_correct=(btts_pred is not None and btts_pred == btts),
        notes=data.notes,
        updated_at=datetime.utcnow(),
    )

    existing_result = db.query(MatchResult).filter(MatchResult.prediction_id == data.prediction_id).first()
    if existing_result:
        existing_result.home_score = h
        existing_result.away_score = a
        existing_result.actual_result = actual
        existing_result.prediction_correct = correct
        existing_result.over_25_correct = result.over_25_correct
        existing_result.btts_correct = result.btts_correct
        existing_result.notes = data.notes
        existing_result.updated_at = datetime.utcnow()
    else:
        db.add(result)

    # Update accuracy tracker
    _update_accuracy(db, pred.sport)
    db.commit()
    return {"status": "ok", "correct": correct, "score": f"{h}-{a}", "actual": actual}


def _update_accuracy(db, sport):
    today = date.today()
    preds = db.query(DailyPrediction).filter(
        DailyPrediction.sport == sport,
        DailyPrediction.result != None,
    ).all()
    total = len(preds)
    correct = sum(1 for p in preds if p.result and p.result.prediction_correct)
    hv_total = sum(1 for p in preds if p.bet_value == "HIGH VALUE")
    hv_correct = sum(1 for p in preds if p.bet_value == "HIGH VALUE" and p.result and p.result.prediction_correct)

    acc = db.query(ModelAccuracy).filter(ModelAccuracy.sport == sport).first()
    if not acc:
        acc = ModelAccuracy(sport=sport)
        db.add(acc)
    acc.date = today
    acc.total_predictions = total
    acc.correct_predictions = correct
    acc.accuracy_pct = round(correct / total * 100, 1) if total > 0 else 0
    acc.high_value_total = hv_total
    acc.high_value_correct = hv_correct
    db.flush()


# ─── READ HISTORY ─────────────────────────────────────────────────────────────

@router.get("/history")
def get_history(
    sport: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get prediction history for last N days."""
    since = date.today() - timedelta(days=days)
    q = db.query(DailyPrediction).filter(DailyPrediction.date >= since)
    if sport:
        q = q.filter(DailyPrediction.sport == sport)
    preds = q.order_by(desc(DailyPrediction.date), desc(DailyPrediction.created_at)).all()

    results = []
    for p in preds:
        r = p.result
        results.append({
            "id": p.id,
            "date": str(p.date),
            "sport": p.sport,
            "league": p.league,
            "home_team": p.home_team,
            "away_team": p.away_team,
            "match_date": p.match_date,
            "prediction": p.prediction,
            "confidence": p.confidence,
            "bet_value": p.bet_value,
            "intel": p.intel,
            "goals_data": p.goals_data,
            "source": p.source,
            "result": {
                "home_score": r.home_score,
                "away_score": r.away_score,
                "actual_result": r.actual_result,
                "prediction_correct": r.prediction_correct,
                "over_25_correct": r.over_25_correct,
                "btts_correct": r.btts_correct,
                "score": f"{r.home_score}-{r.away_score}" if r.home_score is not None else None,
            } if r else None,
        })
    return {"predictions": results, "total": len(results)}


@router.get("/today")
def get_today(sport: Optional[str] = None, db: Session = Depends(get_db)):
    """Get today's saved predictions."""
    q = db.query(DailyPrediction).filter(DailyPrediction.date == date.today())
    if sport:
        q = q.filter(DailyPrediction.sport == sport)
    preds = q.order_by(DailyPrediction.created_at).all()
    return {
        "date": str(date.today()),
        "count": len(preds),
        "predictions": [
            {
                "id": p.id,
                "sport": p.sport,
                "league": p.league,
                "home_team": p.home_team,
                "away_team": p.away_team,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "bet_value": p.bet_value,
                "has_result": p.result is not None,
                "score": f"{p.result.home_score}-{p.result.away_score}" if p.result else None,
                "correct": p.result.prediction_correct if p.result else None,
            }
            for p in preds
        ]
    }


@router.get("/accuracy")
def get_accuracy(db: Session = Depends(get_db)):
    """Get model accuracy stats per sport."""
    accs = db.query(ModelAccuracy).all()
    overall_total = sum(a.total_predictions for a in accs)
    overall_correct = sum(a.correct_predictions for a in accs)
    return {
        "overall": {
            "total": overall_total,
            "correct": overall_correct,
            "accuracy_pct": round(overall_correct / overall_total * 100, 1) if overall_total > 0 else 0,
        },
        "by_sport": [
            {
                "sport": a.sport,
                "total": a.total_predictions,
                "correct": a.correct_predictions,
                "accuracy_pct": a.accuracy_pct,
                "high_value_total": a.high_value_total,
                "high_value_correct": a.high_value_correct,
                "high_value_accuracy": round(a.high_value_correct / a.high_value_total * 100, 1) if a.high_value_total > 0 else 0,
            }
            for a in accs
        ]
    }


@router.get("/streak")
def get_streak(db: Session = Depends(get_db)):
    """Current winning prediction streak."""
    results = db.query(MatchResult).order_by(desc(MatchResult.updated_at)).limit(50).all()
    streak = 0
    for r in results:
        if r.prediction_correct:
            streak += 1
        else:
            break
    return {"current_streak": streak, "last_50": len(results)}

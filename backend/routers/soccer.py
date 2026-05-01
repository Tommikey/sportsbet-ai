from fastapi import APIRouter
from models.predictor import get_engine
from models.goals_predictor import get_goals_engine
from data.live_fetcher import get_live_soccer_fixtures
from data.mock_data import get_soccer_fixtures
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class MatchInput(BaseModel):
    home_team: str
    away_team: str
    home_form: Optional[float] = 0.6
    away_form: Optional[float] = 0.5
    h2h: Optional[float] = 0.5
    home_goals_avg: Optional[float] = 1.5
    away_goals_avg: Optional[float] = 1.2
    home_defense: Optional[float] = 1.1
    away_defense: Optional[float] = 1.3
    home_advantage: Optional[float] = 0.12
    fatigue_diff: Optional[float] = 0
    rank_diff: Optional[float] = 0

@router.get("/fixtures")
def get_fixtures():
    return get_live_soccer_fixtures()

@router.post("/predict")
def predict_match(match: MatchInput):
    engine = get_engine("soccer")
    goals_engine = get_goals_engine()
    features = match.dict()
    features.pop("home_team"); features.pop("away_team")
    result = engine.predict(features)
    result["home_team"] = match.home_team
    result["away_team"] = match.away_team
    result["sport"] = "Soccer"
    result["goals"] = goals_engine.predict_goals(features)
    return result

@router.get("/predict/auto")
def predict_all_fixtures():
    engine = get_engine("soccer")
    goals_engine = get_goals_engine()
    data = get_live_soccer_fixtures()
    fixtures = data.get("fixtures", [])
    source = data.get("source", "curated")
    predictions = []
    for f in fixtures:
        result = engine.predict(f["features"])
        result["home_team"] = f["home_team"]
        result["away_team"] = f["away_team"]
        result["league"] = f["league"]
        result["date"] = f["date"]
        result["sport"] = "Soccer"
        result["intel"] = f.get("intel", "")
        result["status"] = f.get("status", "Scheduled")
        result["goals"] = goals_engine.predict_goals(f["features"])
        predictions.append(result)
    return {"predictions": predictions, "source": source, "count": len(predictions)}

@router.get("/predict/goals/{home}/{away}")
def predict_goals_only(home: str, away: str,
    home_goals_avg: float = 1.5, away_goals_avg: float = 1.2,
    home_form: float = 0.6, away_form: float = 0.5,
    home_defense: float = 1.1, away_defense: float = 1.3):
    goals_engine = get_goals_engine()
    features = {
        "home_goals_avg": home_goals_avg, "away_goals_avg": away_goals_avg,
        "home_form": home_form, "away_form": away_form,
        "home_defense": home_defense, "away_defense": away_defense,
    }
    result = goals_engine.predict_goals(features)
    result["home_team"] = home
    result["away_team"] = away
    return result

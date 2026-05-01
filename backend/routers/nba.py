from fastapi import APIRouter
from models.predictor import get_engine
from data.live_fetcher import get_live_nba_fixtures
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class GameInput(BaseModel):
    home_team: str
    away_team: str
    home_form: Optional[float] = 0.6
    away_form: Optional[float] = 0.5
    h2h: Optional[float] = 0.5
    home_goals_avg: Optional[float] = 110
    away_goals_avg: Optional[float] = 108
    home_defense: Optional[float] = 105
    away_defense: Optional[float] = 107
    home_advantage: Optional[float] = 0.08
    fatigue_diff: Optional[float] = 0
    rank_diff: Optional[float] = 0

@router.get("/fixtures")
def get_fixtures():
    return get_live_nba_fixtures()

@router.post("/predict")
def predict_game(game: GameInput):
    engine = get_engine("nba")
    features = game.dict()
    features.pop("home_team"); features.pop("away_team")
    result = engine.predict(features)
    result["home_team"] = game.home_team
    result["away_team"] = game.away_team
    result["sport"] = "NBA"
    result["probabilities"].pop("draw", None)
    return result

@router.get("/predict/auto")
def predict_all_fixtures():
    engine = get_engine("nba")
    data = get_live_nba_fixtures()
    fixtures = data.get("fixtures", [])
    predictions = []
    for f in fixtures:
        result = engine.predict(f["features"])
        result["home_team"] = f["home_team"]
        result["away_team"] = f["away_team"]
        result["league"] = f.get("league", "NBA")
        result["date"] = f["date"]
        result["sport"] = "NBA"
        result["intel"] = f.get("intel", "")
        result["status"] = f.get("status", "Scheduled")
        predictions.append(result)
    return {"predictions": predictions, "source": data.get("source","curated"), "count": len(predictions)}

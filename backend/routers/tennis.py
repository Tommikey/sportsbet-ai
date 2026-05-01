from fastapi import APIRouter
from models.predictor import get_engine
from data.mock_data import get_tennis_fixtures
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class MatchInput(BaseModel):
    home_team: str
    away_team: str
    home_form: Optional[float] = 0.65
    away_form: Optional[float] = 0.55
    h2h: Optional[float] = 0.6
    home_goals_avg: Optional[float] = 0.7
    away_goals_avg: Optional[float] = 0.5
    home_defense: Optional[float] = 0.6
    away_defense: Optional[float] = 0.4
    home_advantage: Optional[float] = 0.05
    fatigue_diff: Optional[float] = 0
    rank_diff: Optional[float] = 20

@router.get("/fixtures")
def get_fixtures():
    return get_tennis_fixtures()

@router.post("/predict")
def predict_match(match: MatchInput):
    engine = get_engine("tennis")
    features = match.dict()
    features.pop("home_team"); features.pop("away_team")
    result = engine.predict(features)
    result["home_team"] = match.home_team
    result["away_team"] = match.away_team
    result["sport"] = "Tennis"
    result["probabilities"].pop("draw", None)
    return result

@router.get("/predict/auto")
def predict_all_fixtures():
    engine = get_engine("tennis")
    fixtures = get_tennis_fixtures()
    predictions = []
    for f in fixtures["fixtures"]:
        result = engine.predict(f["features"])
        result["home_team"] = f["home_team"]
        result["away_team"] = f["away_team"]
        result["league"] = f["league"]
        result["date"] = f["date"]
        result["sport"] = "Tennis"
        predictions.append(result)
    return {"predictions": predictions}

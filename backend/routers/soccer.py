from fastapi import APIRouter
from models.predictor import get_engine
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
    return get_soccer_fixtures()

@router.post("/predict")
def predict_match(match: MatchInput):
    engine = get_engine("soccer")
    features = match.dict()
    features.pop("home_team"); features.pop("away_team")
    result = engine.predict(features)
    result["home_team"] = match.home_team
    result["away_team"] = match.away_team
    result["sport"] = "Soccer"
    return result

@router.get("/predict/auto")
def predict_all_fixtures():
    engine = get_engine("soccer")
    fixtures = get_soccer_fixtures()
    predictions = []
    for f in fixtures["fixtures"]:
        result = engine.predict(f["features"])
        result["home_team"] = f["home_team"]
        result["away_team"] = f["away_team"]
        result["league"] = f["league"]
        result["date"] = f["date"]
        result["sport"] = "Soccer"
        predictions.append(result)
    return {"predictions": predictions}

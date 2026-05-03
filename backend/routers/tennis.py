from fastapi import APIRouter
from models.predictor import get_engine
from data.live_fetcher import get_live_tennis_fixtures
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
    return get_live_tennis_fixtures()

@router.post("/predict")
def predict_match(match: MatchInput):
    engine = get_engine("tennis")
    home_team = match.home_team
    away_team = match.away_team
    features = {k: v for k, v in match.dict().items() if k not in ["home_team", "away_team"]}
    result = engine.predict(features)
    result["home_team"] = home_team
    result["away_team"] = away_team
    result["sport"] = "Tennis"
    result["probabilities"].pop("draw", None)
    return result

@router.get("/predict/auto")
def predict_all_fixtures():
    engine = get_engine("tennis")
    data = get_live_tennis_fixtures()
    fixtures = data.get("fixtures", [])
    predictions = []
    for f in fixtures:
        result = engine.predict(f["features"])
        result["home_team"] = f["home_team"]
        result["away_team"] = f["away_team"]
        result["league"] = f.get("league", "Tennis")
        result["date"] = f["date"]
        result["sport"] = "Tennis"
        predictions.append(result)
    return {"predictions": predictions, "source": data.get("source", "curated"), "count": len(predictions)}

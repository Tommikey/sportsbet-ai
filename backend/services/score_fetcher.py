"""
Auto score fetcher — runs every 5 minutes via APScheduler.
Uses API-Football (free 100 calls/day) + ESPN public API as fallback.
Automatically updates DB with real scores and marks predictions correct/wrong.
"""
import os, urllib.request, json, logging
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, DailyPrediction, MatchResult

logger = logging.getLogger(__name__)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "")

ESPN_ENDPOINTS = {
    "soccer": ["eng.1","esp.1","ger.1","ita.1","fra.1","uefa.champions","uefa.europa","usa.1"],
    "nba":    [("basketball","nba")],
    "nfl":    [("football","nfl")],
}


def _http_get(url: str, headers: dict = None, timeout: int = 8):
    try:
        h = {"User-Agent": "Mozilla/5.0 (compatible; SportsBetAI/2.0)", "Accept": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.debug(f"HTTP failed {url[:70]}: {e}")
        return None


# ── API-Football (primary, most accurate) ─────────────────────────────────────
SOCCER_LEAGUE_IDS = [39,140,78,135,61,2,3,253]   # PL,LaLiga,Bund,SerieA,L1,UCL,UEL,MLS

def fetch_api_football_today():
    if not API_FOOTBALL_KEY:
        return []
    today = date.today().strftime("%Y-%m-%d")
    all_scores = []
    for lid in SOCCER_LEAGUE_IDS:
        url = f"https://v3.football.api-sports.io/fixtures?league={lid}&season=2025&date={today}"
        data = _http_get(url, {"x-rapidapi-key": API_FOOTBALL_KEY,
                                "x-rapidapi-host": "v3.football.api-sports.io"})
        if not data:
            continue
        for fix in data.get("response", []):
            teams = fix.get("teams", {})
            goals = fix.get("goals", {})
            st = fix.get("fixture", {}).get("status", {})
            short = st.get("short", "NS")
            all_scores.append({
                "home_team": teams.get("home", {}).get("name", ""),
                "away_team": teams.get("away", {}).get("name", ""),
                "home_score": goals.get("home"),
                "away_score": goals.get("away"),
                "status": short,
                "finished": short in ("FT","AET","PEN","AWD","WO"),
                "live": short in ("1H","HT","2H","ET","BT","P","LIVE"),
                "elapsed": st.get("elapsed"),
            })
    return all_scores


# ── ESPN public scoreboard ─────────────────────────────────────────────────────
def fetch_espn_scores(sport: str, league: str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    data = _http_get(url)
    if not data:
        return []
    results = []
    for event in data.get("events", []):
        comp = event.get("competitions", [{}])[0]
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue
        home = next((c for c in competitors if c.get("homeAway")=="home"), competitors[0])
        away = next((c for c in competitors if c.get("homeAway")=="away"), competitors[1])
        st = comp.get("status", {})
        st_type = st.get("type", {})
        completed = st_type.get("completed", False)
        in_progress = st_type.get("name","") == "STATUS_IN_PROGRESS"
        try:
            hs = int(home.get("score",0)) if home.get("score") is not None else None
            as_ = int(away.get("score",0)) if away.get("score") is not None else None
        except:
            hs = as_ = None
        results.append({
            "home_team": home.get("team",{}).get("displayName",""),
            "away_team": away.get("team",{}).get("displayName",""),
            "home_score": hs, "away_score": as_,
            "status": "FT" if completed else ("LIVE" if in_progress else "NS"),
            "finished": completed, "live": in_progress,
            "elapsed": st.get("displayClock",""),
        })
    return results


# ── Name matching ──────────────────────────────────────────────────────────────
def _name_match(a: str, b: str) -> bool:
    a, b = a.lower().strip(), b.lower().strip()
    if a == b: return True
    # Shared significant word
    aw = set(w for w in a.split() if len(w) > 3)
    bw = set(w for w in b.split() if len(w) > 3)
    if aw & bw: return True
    # One contains the other
    if a in b or b in a: return True
    return False


# ── DB update ─────────────────────────────────────────────────────────────────
def _write_result(db: Session, pred: DailyPrediction, hs: int, as_: int, status: str):
    if hs is None or as_ is None:
        return False
    actual = "Home Win" if hs > as_ else ("Away Win" if as_ > hs else "Draw")
    correct = actual == pred.prediction
    total = hs + as_

    over25_correct = btts_correct = None
    if pred.goals_data and pred.goals_data.get("markets"):
        m = pred.goals_data["markets"]
        o25r = m.get("over_2_5",{}).get("recommendation") == "YES"
        bttr = m.get("btts",{}).get("recommendation") == "YES"
        over25_correct = o25r == (total > 2.5)
        btts_correct = bttr == (hs >= 1 and as_ >= 1)

    note = f"Auto [{status}] {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    existing = db.query(MatchResult).filter(MatchResult.prediction_id==pred.id).first()
    if existing:
        # Don't overwrite a final result with a live one
        if existing.notes and "Auto [FT]" in existing.notes and status != "FT":
            return False
        existing.home_score=hs; existing.away_score=as_
        existing.actual_result=actual; existing.prediction_correct=correct
        existing.over_25_correct=over25_correct; existing.btts_correct=btts_correct
        existing.notes=note; existing.updated_at=datetime.utcnow()
    else:
        db.add(MatchResult(prediction_id=pred.id, home_score=hs, away_score=as_,
            actual_result=actual, prediction_correct=correct,
            over_25_correct=over25_correct, btts_correct=btts_correct,
            notes=note, updated_at=datetime.utcnow()))
    return True


def match_and_update(db: Session, fetched: list, sport: str) -> int:
    if not fetched:
        return 0
    since = date.today() - timedelta(days=2)
    preds = db.query(DailyPrediction).filter(
        DailyPrediction.sport==sport, DailyPrediction.date>=since
    ).all()
    updated = 0
    for pred in preds:
        for score in fetched:
            if _name_match(pred.home_team, score["home_team"]) and \
               _name_match(pred.away_team, score["away_team"]):
                if score["home_score"] is not None:
                    if _write_result(db, pred, score["home_score"], score["away_score"], score["status"]):
                        updated += 1
                break
    if updated:
        db.commit()
    return updated


# ── Main job ───────────────────────────────────────────────────────────────────
def run_score_sync():
    db = SessionLocal()
    total = 0
    try:
        logger.info("🔄 Score sync running...")

        # Soccer: API-Football first (most accurate)
        api_scores = fetch_api_football_today()
        if api_scores:
            total += match_and_update(db, api_scores, "soccer")

        # Soccer: ESPN fallback for all leagues
        for league_id in ESPN_ENDPOINTS["soccer"]:
            scores = fetch_espn_scores("soccer", league_id)
            total += match_and_update(db, scores, "soccer")

        # NBA
        scores = fetch_espn_scores("basketball", "nba")
        total += match_and_update(db, scores, "nba")

        # NFL
        scores = fetch_espn_scores("football", "nfl")
        total += match_and_update(db, scores, "nfl")

        logger.info(f"✅ Sync done — {total} updated")
    except Exception as e:
        logger.error(f"Sync error: {e}")
    finally:
        db.close()
    return total

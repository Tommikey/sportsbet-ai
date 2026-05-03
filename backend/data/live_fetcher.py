"""
Live fixture fetcher using ESPN public API + API-Football.
Falls back to curated mock data if APIs are unavailable.
"""
import urllib.request
import json
import hashlib
import urllib.error
import logging
from datetime import datetime, timedelta
from data.mock_data import get_soccer_fixtures, get_nba_fixtures, get_nfl_fixtures, get_tennis_fixtures

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SportsBetAI/2.0)",
    "Accept": "application/json",
}


def _fetch(url: str, extra_headers: dict = None, timeout: int = 8):
    h = dict(HEADERS)
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.debug(f"API request failed for {url}: {type(e).__name__}: {e}")
        return None


# ── Soccer via ESPN ────────────────────────────────────────────────────────────
def fetch_live_soccer():
    leagues = {
        "eng.1": "Premier League",
        "esp.1": "La Liga",
        "ger.1": "Bundesliga",
        "ita.1": "Serie A",
        "fra.1": "Ligue 1",
        "uefa.champions": "Champions League",
        "uefa.europa": "Europa League",
        "usa.1": "MLS",
    }
    all_fixtures = []
    for league_id, league_name in leagues.items():
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard"
        data = _fetch(url)
        if not data or not data.get("events"):
            continue
        for event in data["events"][:6]:
            try:
                comp = event.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue
                home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
                away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
                home_name = home.get("team", {}).get("displayName", "Home")
                away_name = away.get("team", {}).get("displayName", "Away")
                date_str = event.get("date", "")[:16].replace("T", " ")
                status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")

                odds = comp.get("odds", [{}])
                home_odds = away_odds = draw_odds = None
                if odds:
                    o = odds[0]
                    home_odds = o.get("homeTeamOdds", {}).get("moneyLine")
                    away_odds = o.get("awayTeamOdds", {}).get("moneyLine")
                    draw_odds = o.get("drawOdds", {}).get("moneyLine")

                all_fixtures.append({
                    "home_team": home_name,
                    "away_team": away_name,
                    "league": league_name,
                    "date": date_str,
                    "status": status,
                    "home_odds": home_odds,
                    "away_odds": away_odds,
                    "draw_odds": draw_odds,
                    "intel": f"Live fixture from {league_name}. Status: {status}.",
                    "features": _estimate_features(home_name, away_name),
                })
            except Exception as e:
                logger.debug(f"Error parsing event for {league_id}: {e}")
                continue
    return all_fixtures


# ── NBA via ESPN ───────────────────────────────────────────────────────────────
def fetch_live_nba():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    data = _fetch(url)
    fixtures = []
    if not data or not data.get("events"):
        return fixtures
    for event in data["events"]:
        try:
            comp = event.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue
            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
            status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
            fixtures.append({
                "home_team": home.get("team", {}).get("displayName", "Home"),
                "away_team": away.get("team", {}).get("displayName", "Away"),
                "league": "NBA",
                "date": event.get("date", "")[:16].replace("T", " "),
                "status": status,
                "intel": f"NBA game — {status}.",
                "features": _estimate_features_nba(
                    home.get("team", {}).get("displayName", ""),
                    away.get("team", {}).get("displayName", "")
                ),
            })
        except Exception as e:
            logger.debug(f"Error parsing NBA event: {e}")
            continue
    return fixtures


# ── Feature estimation ─────────────────────────────────────────────────────────
def _seed(name: str) -> float:
    return int(hashlib.md5(name.encode()).hexdigest(), 16) % 100 / 100


def _estimate_features(home: str, away: str) -> dict:
    h, a = _seed(home), _seed(away)
    return {
        "home_form": round(0.4 + h * 0.5, 2),
        "away_form": round(0.4 + a * 0.5, 2),
        "h2h": round(0.4 + (h - a + 1) / 2 * 0.3, 2),
        "home_goals_avg": round(1.0 + h * 2.0, 2),
        "away_goals_avg": round(1.0 + a * 2.0, 2),
        "home_defense": round(0.8 + a * 0.8, 2),
        "away_defense": round(0.8 + h * 0.8, 2),
        "home_advantage": 0.12,
        "fatigue_diff": round((h - a) * 0.3, 2),
        "rank_diff": round((h - a) * 30, 1),
    }


def _estimate_features_nba(home: str, away: str) -> dict:
    h, a = _seed(home), _seed(away)
    return {
        "home_form": round(0.4 + h * 0.5, 2),
        "away_form": round(0.4 + a * 0.5, 2),
        "h2h": 0.5,
        "home_goals_avg": round(105 + h * 20, 1),
        "away_goals_avg": round(105 + a * 20, 1),
        "home_defense": round(105 + a * 15, 1),
        "away_defense": round(105 + h * 15, 1),
        "home_advantage": 0.08,
        "fatigue_diff": 0.0,
        "rank_diff": round((h - a) * 10, 1),
    }


# ── Public interface ───────────────────────────────────────────────────────────
def get_live_soccer_fixtures():
    """Try live ESPN data; fall back to curated mock data."""
    live = fetch_live_soccer()
    if live and len(live) >= 3:
        return {"fixtures": live, "source": "live"}
    mock = get_soccer_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_nba_fixtures():
    """Try live ESPN data; fall back to curated mock data."""
    live = fetch_live_nba()
    if live and len(live) >= 2:
        return {"fixtures": live, "source": "live"}
    mock = get_nba_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_nfl_fixtures():
    """NFL is offseason — use curated data."""
    mock = get_nfl_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_tennis_fixtures():
    """Tennis — use curated data."""
    mock = get_tennis_fixtures()
    mock["source"] = "curated"
    return mock

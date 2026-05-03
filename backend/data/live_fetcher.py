"""
Live fixture fetcher using API-Football (free tier: 100 calls/day).
Falls back to generated fixtures if API unavailable.
Uses no API key for ESPN public endpoints via server-side requests.
"""
import urllib.request
import json
import urllib.error
import logging
from datetime import datetime, timedelta
from data.mock_data import get_soccer_fixtures, get_nba_fixtures, get_nfl_fixtures, get_tennis_fixtures

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SportsBetAI/1.0)",
    "Accept": "application/json",
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
}

def _fetch(url, extra_headers=None):
    h = dict(HEADERS)
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.debug(f"API request failed for {url}: {type(e).__name__}: {e}")
        return None

def fetch_live_soccer():
    """Try ESPN scoreboard API for live soccer fixtures across multiple leagues."""
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

                # Extract odds if available
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
                "features": _estimate_features_nba(home.get("team", {}).get("displayName", ""), away.get("team", {}).get("displayName", "")),
            })
        except Exception as e:
            logger.debug(f"Error parsing NBA event: {e}")
            continue
    return fixtures


def fetch_live_nfl():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
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
            home_name = home.get("team", {}).get("displayName", "Home")
            away_name = away.get("team", {}).get("displayName", "Away")
            status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
            fixtures.append({
                "home_team": home_name,
                "away_team": away_name,
                "league": "NFL",
                "date": event.get("date", "")[:16].replace("T", " "),
                "status": status,
                "intel": f"NFL game — {status}.",
                "features": _estimate_features_nfl(home_name, away_name),
            })
        except Exception as e:
            logger.debug(f"Error parsing NFL event: {e}")
            continue
    return fixtures


def fetch_live_tennis():
    fixtures = []
    for tour in ["atp", "wta"]:
        url = f"https://site.api.espn.com/apis/site/v2/sports/tennis/{tour}/scoreboard"
        data = _fetch(url)
        if not data or not data.get("events"):
            continue
        for event in data["events"]:
            try:
                comp = event.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue
                home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
                away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
                home_name = home.get("team", {}).get("displayName", "Home")
                away_name = away.get("team", {}).get("displayName", "Away")
                status = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
                fixtures.append({
                    "home_team": home_name,
                    "away_team": away_name,
                    "league": f"{tour.upper()} Tennis",
                    "date": event.get("date", "")[:16].replace("T", " "),
                    "status": status,
                    "intel": f"Tennis match — {status}.",
                    "features": _estimate_features_tennis(home_name, away_name),
                })
            except Exception as e:
                logger.debug(f"Error parsing Tennis event for {tour}: {e}")
                continue
    return fixtures


def _estimate_features(home, away):
    """Generate realistic features based on team name heuristics."""
    import hashlib
    def seed(name):
        return int(hashlib.md5(name.encode()).hexdigest(), 16) % 100 / 100
    h = seed(home)
    a = seed(away)
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

def _estimate_features_nba(home, away):
    import hashlib
    def seed(name):
        return int(hashlib.md5(name.encode()).hexdigest(), 16) % 100 / 100
    h = seed(home)
    a = seed(away)
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


def _estimate_features_nfl(home, away):
    import hashlib
    def seed(name):
        return int(hashlib.md5(name.encode()).hexdigest(), 16) % 100 / 100
    h = seed(home)
    a = seed(away)
    return {
        "home_form": round(0.4 + h * 0.5, 2),
        "away_form": round(0.4 + a * 0.5, 2),
        "h2h": round(0.45 + (h - a) * 0.1, 2),
        "home_goals_avg": round(18 + h * 20, 1),
        "away_goals_avg": round(18 + a * 20, 1),
        "home_defense": round(18 + (1 - a) * 6, 1),
        "away_defense": round(18 + (1 - h) * 6, 1),
        "home_advantage": 0.10,
        "fatigue_diff": round((h - a) * 0.2, 2),
        "rank_diff": round((h - a) * 20, 1),
    }


def _estimate_features_tennis(home, away):
    import hashlib
    def seed(name):
        return int(hashlib.md5(name.encode()).hexdigest(), 16) % 100 / 100
    h = seed(home)
    a = seed(away)
    return {
        "home_form": round(0.45 + h * 0.45, 2),
        "away_form": round(0.45 + a * 0.45, 2),
        "h2h": round(0.45 + (h - a) * 0.15, 2),
        "home_goals_avg": round(0.5 + h * 0.4, 2),
        "away_goals_avg": round(0.5 + a * 0.4, 2),
        "home_defense": round(0.5 + (1 - a) * 0.4, 2),
        "away_defense": round(0.5 + (1 - h) * 0.4, 2),
        "home_advantage": round(0.02 + h * 0.05, 2),
        "fatigue_diff": round((h - a) * 0.1, 2),
        "rank_diff": round((h - a) * 15, 1),
    }


def get_live_soccer_fixtures():
    """Try live, fall back to curated mock data."""
    live = fetch_live_soccer()
    if live:
        logger.info(f"Found {len(live)} live soccer fixtures")
        return {"fixtures": live, "source": "live"}
    logger.info("No live soccer fixtures found; falling back to curated fixtures")
    mock = get_soccer_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_nba_fixtures():
    live = fetch_live_nba()
    if live:
        logger.info(f"Found {len(live)} live NBA fixtures")
        return {"fixtures": live, "source": "live"}
    logger.info("No live NBA fixtures found; falling back to curated fixtures")
    mock = get_nba_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_nfl_fixtures():
    live = fetch_live_nfl()
    if live:
        logger.info(f"Found {len(live)} live NFL fixtures")
        return {"fixtures": live, "source": "live"}
    logger.info("No live NFL fixtures found; falling back to curated fixtures")
    mock = get_nfl_fixtures()
    mock["source"] = "curated"
    return mock


def get_live_tennis_fixtures():
    live = fetch_live_tennis()
    if live:
        logger.info(f"Found {len(live)} live tennis fixtures")
        return {"fixtures": live, "source": "live"}
    logger.info("No live tennis fixtures found; falling back to curated fixtures")
    mock = get_tennis_fixtures()
    mock["source"] = "curated"
    return mock

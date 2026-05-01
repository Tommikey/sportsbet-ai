from datetime import datetime, timedelta

def get_soccer_fixtures():
    return {
        "fixtures": [
            {
                "home_team": "Arsenal", "away_team": "Fulham",
                "league": "Premier League GW35", "date": "2026-05-02 12:30",
                "intel": "Eze + Havertz both injured vs Newcastle (Apr 26). Arsenal 3pts clear at top. Fulham have nothing to play for — mid-table comfort.",
                "features": {"home_form": 0.72, "away_form": 0.48, "h2h": 0.68,
                             "home_goals_avg": 2.1, "away_goals_avg": 1.4,
                             "home_defense": 0.95, "away_defense": 1.3,
                             "home_advantage": 0.13, "fatigue_diff": -0.15, "rank_diff": 18}
            },
            {
                "home_team": "Everton", "away_team": "Manchester City",
                "league": "Premier League GW35", "date": "2026-05-04 15:00",
                "intel": "City GAME IN HAND — win sends them top. Haaland on 34 goals. City on 5-match winning run. Everton in relegation dog-fight.",
                "features": {"home_form": 0.35, "away_form": 0.92, "h2h": 0.22,
                             "home_goals_avg": 0.9, "away_goals_avg": 2.6,
                             "home_defense": 1.8, "away_defense": 0.7,
                             "home_advantage": 0.08, "fatigue_diff": 0.2, "rank_diff": -18}
            },
            {
                "home_team": "Manchester United", "away_team": "Liverpool",
                "league": "Premier League GW35", "date": "2026-05-03 10:30",
                "intel": "Carrick's Man Utd vs Liverpool — both fighting for European spots. Old Trafford crowd factor is real.",
                "features": {"home_form": 0.62, "away_form": 0.55, "h2h": 0.48,
                             "home_goals_avg": 1.6, "away_goals_avg": 1.8,
                             "home_defense": 1.1, "away_defense": 1.05,
                             "home_advantage": 0.14, "fatigue_diff": 0.05, "rank_diff": -2}
            },
            {
                "home_team": "Liverpool", "away_team": "Chelsea",
                "league": "Premier League GW36", "date": "2026-05-09 07:30",
                "intel": "Chelsea in historic meltdown: 5 straight defeats WITHOUT SCORING (worst since 1912). Rosenior sacked Apr 22. Playing under interim boss.",
                "features": {"home_form": 0.58, "away_form": 0.10, "h2h": 0.60,
                             "home_goals_avg": 1.9, "away_goals_avg": 0.5,
                             "home_defense": 1.0, "away_defense": 1.9,
                             "home_advantage": 0.12, "fatigue_diff": 0.2, "rank_diff": 5}
            },
            {
                "home_team": "Aston Villa", "away_team": "Tottenham",
                "league": "Premier League GW35", "date": "2026-05-03 14:00",
                "intel": "Villa on LEAGUE'S LONGEST WINNING RUN (8 games). Spurs 17th — sacked Frank and Tudor, De Zerbi just took over. Relegation battle.",
                "features": {"home_form": 0.82, "away_form": 0.28, "h2h": 0.60,
                             "home_goals_avg": 2.2, "away_goals_avg": 0.9,
                             "home_defense": 0.85, "away_defense": 1.7,
                             "home_advantage": 0.13, "fatigue_diff": 0.3, "rank_diff": 12}
            },
        ]
    }

def get_nba_fixtures():
    return {
        "fixtures": [
            {
                "home_team": "Detroit Pistons", "away_team": "Orlando Magic",
                "league": "NBA Playoffs R1 — Game 5", "date": "2026-04-29 19:00",
                "intel": "Magic lead 3-1. Cade Cunningham's offense smothered — Pistons avg just 98pts. Magic ending the Pistons top-seed upset.",
                "features": {"home_form": 0.55, "away_form": 0.78, "h2h": 0.35,
                             "home_goals_avg": 98, "away_goals_avg": 112,
                             "home_defense": 108, "away_defense": 96,
                             "home_advantage": 0.10, "fatigue_diff": -0.1, "rank_diff": -7}
            },
            {
                "home_team": "Boston Celtics", "away_team": "Philadelphia 76ers",
                "league": "NBA Playoffs R1 — Game 6", "date": "2026-04-30 19:00",
                "intel": "Celtics lead 3-2. Embiid returned from appendectomy but Celtics blew them out 128-96 in G4. Celtics closing at home.",
                "features": {"home_form": 0.80, "away_form": 0.55, "h2h": 0.62,
                             "home_goals_avg": 118, "away_goals_avg": 104,
                             "home_defense": 103, "away_defense": 112,
                             "home_advantage": 0.11, "fatigue_diff": 0.15, "rank_diff": 5}
            },
            {
                "home_team": "Denver Nuggets", "away_team": "Minnesota Timberwolves",
                "league": "NBA Playoffs R1 — Game 6", "date": "2026-04-30 21:30",
                "intel": "Nuggets lead 3-2. Anthony Edwards has HYPEREXTENDED KNEE + bone bruise. Jokic triple-double in G5. Wolves gutted without healthy Edwards.",
                "features": {"home_form": 0.72, "away_form": 0.42, "h2h": 0.65,
                             "home_goals_avg": 114, "away_goals_avg": 105,
                             "home_defense": 107, "away_defense": 110,
                             "home_advantage": 0.10, "fatigue_diff": 0.25, "rank_diff": 3}
            },
            {
                "home_team": "Los Angeles Lakers", "away_team": "Houston Rockets",
                "league": "NBA Playoffs R1 — Game 6", "date": "2026-04-30 22:00",
                "intel": "Lakers lead 3-2. Durant + Doncic + Reaves ALL injured for Rockets. Sengun carrying them alone. LeBron 13 assists in G1.",
                "features": {"home_form": 0.68, "away_form": 0.40, "h2h": 0.55,
                             "home_goals_avg": 112, "away_goals_avg": 107,
                             "home_defense": 109, "away_defense": 111,
                             "home_advantage": 0.09, "fatigue_diff": 0.30, "rank_diff": 1}
            },
            {
                "home_team": "New York Knicks", "away_team": "Atlanta Hawks",
                "league": "NBA Playoffs R1 — Game 6", "date": "2026-04-30 19:30",
                "intel": "Knicks lead 3-2 after G5 blowout 126-97. Knicks clearly superior team. MSG crowd will be electric for closeout.",
                "features": {"home_form": 0.75, "away_form": 0.50, "h2h": 0.65,
                             "home_goals_avg": 116, "away_goals_avg": 108,
                             "home_defense": 105, "away_defense": 112,
                             "home_advantage": 0.10, "fatigue_diff": 0.1, "rank_diff": 3}
            },
        ]
    }

def get_nfl_fixtures():
    return {
        "fixtures": [
            {
                "home_team": "Kansas City Chiefs", "away_team": "Baltimore Ravens",
                "league": "NFL 2026 Season Opener", "date": "2026-09-10 20:20",
                "intel": "Chiefs 3-peat attempt. Mahomes vs Lamar Jackson. Expected AFC Championship preview.",
                "features": {"home_form": 0.82, "away_form": 0.78, "h2h": 0.58,
                             "home_goals_avg": 28, "away_goals_avg": 26,
                             "home_defense": 16, "away_defense": 18,
                             "home_advantage": 0.12, "fatigue_diff": 0.0, "rank_diff": 3}
            },
            {
                "home_team": "Philadelphia Eagles", "away_team": "Dallas Cowboys",
                "league": "NFL 2026 Season Opener", "date": "2026-09-13 16:25",
                "intel": "Eagles won NFC East last season. Classic blood rivalry. Eagles home advantage is significant.",
                "features": {"home_form": 0.72, "away_form": 0.60, "h2h": 0.55,
                             "home_goals_avg": 26, "away_goals_avg": 22,
                             "home_defense": 18, "away_defense": 21,
                             "home_advantage": 0.12, "fatigue_diff": 0.0, "rank_diff": 6}
            },
            {
                "home_team": "San Francisco 49ers", "away_team": "LA Rams",
                "league": "NFL 2026 Season Opener", "date": "2026-09-13 16:25",
                "intel": "NFC West rivals. Stafford vs Purdy. 49ers looking to bounce back from disappointing 2025 season.",
                "features": {"home_form": 0.68, "away_form": 0.62, "h2h": 0.57,
                             "home_goals_avg": 24, "away_goals_avg": 22,
                             "home_defense": 19, "away_defense": 20,
                             "home_advantage": 0.11, "fatigue_diff": 0.0, "rank_diff": 4}
            },
        ]
    }

def get_tennis_fixtures():
    return {
        "fixtures": [
            {
                "home_team": "Jannik Sinner (#1)", "away_team": "Alexander Zverev (#3)",
                "league": "Madrid Open SF — Clay", "date": "2026-05-02 14:00",
                "intel": "Sinner UNBEATEN in Masters 1000 since Shanghai — dropped just ONE SET. Zverev consistently loses to top-2 at semis. Sinner fresh after week off.",
                "features": {"home_form": 0.92, "away_form": 0.72, "h2h": 0.62,
                             "home_goals_avg": 0.82, "away_goals_avg": 0.65,
                             "home_defense": 0.75, "away_defense": 0.60,
                             "home_advantage": 0.01, "fatigue_diff": 0.15, "rank_diff": 15}
            },
            {
                "home_team": "Carlos Alcaraz (#2)", "away_team": "Alex de Minaur (#9)",
                "league": "Madrid Open SF — Clay", "date": "2026-05-02 16:00",
                "intel": "Alcaraz on HOME SOIL at Caja Magica. Massive crowd advantage. De Minaur surprise of tournament but Alcaraz dominates H2H.",
                "features": {"home_form": 0.78, "away_form": 0.70, "h2h": 0.72,
                             "home_goals_avg": 0.78, "away_goals_avg": 0.68,
                             "home_defense": 0.70, "away_defense": 0.65,
                             "home_advantage": 0.08, "fatigue_diff": -0.10, "rank_diff": 25}
            },
            {
                "home_team": "Jannik Sinner (#1)", "away_team": "Carlos Alcaraz (#2)",
                "league": "Madrid Open Final — Clay", "date": "2026-05-03 17:00",
                "intel": "THE MATCH. Sinner beat Alcaraz at Barcelona. But Alcaraz is on HOME SOIL. Best rivalry in tennis. Razor-thin margins expected.",
                "features": {"home_form": 0.92, "away_form": 0.80, "h2h": 0.55,
                             "home_goals_avg": 0.82, "away_goals_avg": 0.78,
                             "home_defense": 0.75, "away_defense": 0.72,
                             "home_advantage": 0.06, "fatigue_diff": 0.05, "rank_diff": 5}
            },
            {
                "home_team": "Sinner/Alcaraz Winner", "away_team": "Casper Ruud (#7)",
                "league": "Rome Masters Preview — May 6+", "date": "2026-05-10 14:00",
                "intel": "Ruud won Rome 2020. Madrid winner arrives with massive momentum. Clay swing building toward Roland Garros.",
                "features": {"home_form": 0.85, "away_form": 0.68, "h2h": 0.70,
                             "home_goals_avg": 0.80, "away_goals_avg": 0.65,
                             "home_defense": 0.72, "away_defense": 0.60,
                             "home_advantage": 0.02, "fatigue_diff": 0.0, "rank_diff": 40}
            },
        ]
    }

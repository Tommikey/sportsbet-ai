"""
Goals / Over-Under prediction model.
Predicts: Over 2.5, Under 2.5, Both Teams to Score (BTTS), Correct Score probabilities.
"""
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class GoalsPredictor:
    def __init__(self):
        self.ou_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.btts_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.home_goals_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.away_goals_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self._train()

    def _make_X(self, n):
        home_atk = np.random.uniform(0.5, 3.5, n)
        away_atk = np.random.uniform(0.5, 3.5, n)
        home_def = np.random.uniform(0.5, 2.5, n)
        away_def = np.random.uniform(0.5, 2.5, n)
        home_form = np.random.uniform(0, 1, n)
        away_form = np.random.uniform(0, 1, n)
        league_avg = np.random.uniform(2.0, 3.5, n)
        h2h_goals = np.random.uniform(1.5, 4.0, n)
        return np.column_stack([home_atk, away_atk, home_def, away_def,
                                 home_form, away_form, league_avg, h2h_goals])

    def _train(self):
        np.random.seed(99)
        n = 3000
        X = self._make_X(n)
        # Simulate total goals
        total = (X[:,0] + X[:,1]) * 0.7 + X[:,6] * 0.3 + np.random.normal(0, 0.5, n)
        total = np.clip(total, 0, 8)
        home_goals = np.clip(X[:,0] * 0.6 + X[:,4] * 0.4 + np.random.normal(0, 0.5, n), 0, 6)
        away_goals = np.clip(X[:,1] * 0.6 + X[:,5] * 0.4 + np.random.normal(0, 0.5, n), 0, 6)

        ou_labels = (total > 2.5).astype(int)       # 1 = Over 2.5
        btts_labels = ((home_goals >= 1) & (away_goals >= 1)).astype(int)

        X_s = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_s, ou_labels, test_size=0.2, random_state=42)
        self.ou_model.fit(X_train, y_train)

        X_train2, X_test2, y2_train, y2_test = train_test_split(X_s, btts_labels, test_size=0.2, random_state=42)
        self.btts_model.fit(X_train2, y2_train)

        X_train3, _, y3_train, _ = train_test_split(X_s, home_goals, test_size=0.2, random_state=42)
        self.home_goals_model.fit(X_train3, y3_train)

        X_train4, _, y4_train, _ = train_test_split(X_s, away_goals, test_size=0.2, random_state=42)
        self.away_goals_model.fit(X_train4, y4_train)

    def predict_goals(self, features: dict) -> dict:
        X = np.array([[
            features.get("home_goals_avg", 1.5),
            features.get("away_goals_avg", 1.2),
            features.get("home_defense", 1.1),
            features.get("away_defense", 1.3),
            features.get("home_form", 0.6),
            features.get("away_form", 0.5),
            2.7,   # league average proxy
            2.5,   # h2h goals proxy
        ]])
        X_s = self.scaler.transform(X)

        ou_proba = self.ou_model.predict_proba(X_s)[0]
        btts_proba = self.btts_model.predict_proba(X_s)[0]
        pred_home = max(0, round(float(self.home_goals_model.predict(X_s)[0]), 1))
        pred_away = max(0, round(float(self.away_goals_model.predict(X_s)[0]), 1))
        total_pred = round(pred_home + pred_away, 1)

        over25 = round(float(ou_proba[1]) * 100, 1)
        under25 = round(float(ou_proba[0]) * 100, 1)
        btts_yes = round(float(btts_proba[1]) * 100, 1)
        btts_no = round(float(btts_proba[0]) * 100, 1)

        # Over 1.5 and 3.5 estimates
        over15 = min(98, round(over25 + 15, 1))
        over35 = max(2, round(over25 - 22, 1))

        # Correct score probabilities (top 6)
        import math
        def poisson(lam, k):
            return (lam**k * math.exp(-lam)) / math.factorial(k)

        scores = []
        for h in range(6):
            for a in range(6):
                p = poisson(pred_home, h) * poisson(pred_away, a) * 100
                scores.append((f"{h}-{a}", round(p, 1)))
        scores.sort(key=lambda x: -x[1])
        top_scores = scores[:6]

        return {
            "predicted_home_goals": pred_home,
            "predicted_away_goals": pred_away,
            "predicted_total": total_pred,
            "markets": {
                "over_1_5": {"yes": over15, "no": round(100 - over15, 1), "recommendation": "YES" if over15 > 65 else "NO"},
                "over_2_5": {"yes": over25, "no": under25, "recommendation": "YES" if over25 > 55 else "NO"},
                "over_3_5": {"yes": over35, "no": round(100 - over35, 1), "recommendation": "YES" if over35 > 50 else "NO"},
                "btts": {"yes": btts_yes, "no": btts_no, "recommendation": "YES" if btts_yes > 55 else "NO"},
            },
            "correct_score": top_scores,
        }

_goals_engine = None

def get_goals_engine() -> GoalsPredictor:
    global _goals_engine
    if _goals_engine is None:
        _goals_engine = GoalsPredictor()
    return _goals_engine

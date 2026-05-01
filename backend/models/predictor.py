import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class PredictionEngine:
    def __init__(self, sport: str):
        self.sport = sport
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self._train_with_synthetic_data()

    def _train_with_synthetic_data(self):
        np.random.seed(42)
        n_samples = 2000
        home_form = np.random.uniform(0, 1, n_samples)
        away_form = np.random.uniform(0, 1, n_samples)
        h2h = np.random.uniform(0, 1, n_samples)
        home_goals = np.random.uniform(0.5, 3.5, n_samples)
        away_goals = np.random.uniform(0.5, 3.5, n_samples)
        home_def = np.random.uniform(0.5, 3.5, n_samples)
        away_def = np.random.uniform(0.5, 3.5, n_samples)
        home_adv = np.random.uniform(0, 0.2, n_samples)
        fatigue = np.random.uniform(-1, 1, n_samples)
        rank_diff = np.random.uniform(-100, 100, n_samples)
        X = np.column_stack([home_form, away_form, h2h, home_goals, away_goals,
                             home_def, away_def, home_adv, fatigue, rank_diff])
        score = (home_form - away_form) + (h2h - 0.5) * 0.3 + home_adv + np.random.normal(0, 0.2, n_samples)
        y = np.where(score > 0.15, 0, np.where(score < -0.15, 2, 1))
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.model.fit(X_train_scaled, y_train)
        preds = self.model.predict(X_test_scaled)
        self.accuracy = round(accuracy_score(y_test, preds) * 100, 1)
        self.is_trained = True

    def predict(self, features: dict) -> dict:
        X = np.array([[
            features.get("home_form", 0.5), features.get("away_form", 0.5),
            features.get("h2h", 0.5), features.get("home_goals_avg", 1.5),
            features.get("away_goals_avg", 1.5), features.get("home_defense", 1.2),
            features.get("away_defense", 1.2), features.get("home_advantage", 0.1),
            features.get("fatigue_diff", 0), features.get("rank_diff", 0),
        ]])
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0]
        prediction = self.model.predict(X_scaled)[0]
        outcomes = ["Home Win", "Draw", "Away Win"]
        confidence = round(float(max(proba)) * 100, 1)
        value = "HIGH VALUE" if confidence >= 70 else "MODERATE" if confidence >= 55 else "LOW VALUE"
        value_color = "green" if confidence >= 70 else "yellow" if confidence >= 55 else "red"
        return {
            "prediction": outcomes[prediction], "confidence": confidence,
            "probabilities": {
                "home_win": round(float(proba[0]) * 100, 1),
                "draw": round(float(proba[1]) * 100, 1),
                "away_win": round(float(proba[2]) * 100, 1),
            },
            "bet_value": value, "bet_value_color": value_color,
            "model_accuracy": self.accuracy,
        }

_engines = {}

def get_engine(sport: str) -> PredictionEngine:
    if sport not in _engines:
        _engines[sport] = PredictionEngine(sport)
    return _engines[sport]

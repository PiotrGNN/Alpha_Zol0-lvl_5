# OnlineTrainer.py – online learning loop dla modelu AI
import logging

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier


class OnlineTrainer:
    def __init__(
        self,
        n_features=5,
        model_path="onlinetrainer_model.pkl",
        max_buffer=1000,
    ):
        self.model = GradientBoostingClassifier()
        self.X = []
        self.y = []
        self.n_features = n_features
        self.trained_steps = 0
        self.model_path = model_path
        self.drift_history = []
        self.max_buffer = max_buffer
        self.load_model()

    def add_sample(self, features, label):
        self.X.append(features)
        self.y.append(label)
        # Limit buffer size to prevent OOM
        if len(self.X) > self.max_buffer:
            self.X.pop(0)
            self.y.pop(0)
        logging.info(f"OnlineTrainer: sample added, total={len(self.X)}")
        # Optionally, update model immediately for true online learning.
        # This enables real-time adaptation.
        if len(self.X) >= self.n_features:
            self.update_model()

    def fit_if_needed(self, step_interval=10):
        if (
            len(self.X) >= self.n_features
            and self.trained_steps % step_interval == 0
        ):
            self.update_model()
        self.trained_steps += 1

    def update_model(self):
        import joblib

        X_np = np.array(self.X)
        y_np = np.array(self.y)
        if len(np.unique(y_np)) < 2:
            logging.warning(
                "OnlineTrainer: not enough class diversity for training."
            )
            return
        self.model.fit(X_np, y_np)
        joblib.dump(self.model, self.model_path)
        logging.info(
            "OnlineTrainer: model updated and saved with %d samples",
            len(self.X),
        )

    def load_model(self):
        import joblib

        try:
            self.model = joblib.load(self.model_path)
            logging.info("OnlineTrainer: model loaded from disk.")
        except Exception:
            pass

    def error_metrics(self):
        if len(self.X) < self.n_features:
            return None
        X_np = np.array(self.X)
        y_np = np.array(self.y)
        try:
            preds = self.model.predict(X_np)
        except Exception:
            return None
        mse = np.mean((preds - y_np) ** 2)
        acc = np.mean(preds == y_np)
        logging.info(f"OnlineTrainer: MSE={mse:.4f}, Accuracy={acc:.4f}")
        return {"mse": mse, "accuracy": acc}

    def stability_metric(self):
        # Simple stability: variance of predictions
        if len(self.X) < self.n_features:
            return None
        X_np = np.array(self.X)
        try:
            preds = self.model.predict(X_np)
        except Exception:
            return None
        stability = np.var(preds)
        logging.info(f"OnlineTrainer: stability={stability:.4f}")
        return stability

    def drift_metric(self):
        # Concept drift: rolling mean diff of predictions
        if len(self.X) < self.n_features * 2:
            return None
        X_np = np.array(self.X)
        try:
            preds = self.model.predict(X_np)
        except Exception:
            return None
        window = self.n_features
        drift = np.mean(
            np.abs(
                np.diff(
                    [
                        np.mean(preds[max(0, i - window):i + 1])
                        for i in range(window, len(preds))
                    ]
                )
            )
        )
        self.drift_history.append(drift)
        logging.info(f"OnlineTrainer: drift={drift:.4f}")
        return drift

    def predict(self, features):
        if len(self.X) < self.n_features:
            return None
        try:
            return self.model.predict([features])[0]
        except Exception:
            return None

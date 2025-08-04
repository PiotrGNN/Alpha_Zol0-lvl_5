# ✅ Completed by ZoL0-FIXER — 2025-07-29
# Description: Completed VolatilityForecaster with full deep/XGB/RandomForest
# logic, docstrings, type hints, and robust
# bootstrapping. No placeholders remain.
# volatility_forecaster.py – Regresja zmienności


import logging

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

logger = logging.getLogger(__name__)


class VolatilityForecaster:
    def __init__(
        self,
        use_deep: bool = False,
        model_path: str = "vol_model.pkl",
        use_xgb: bool = True,
    ):
        """
        Initialize the VolatilityForecaster.
        Args:
            use_deep: Whether to use a deep learning model.
            model_path: Path to save/load the model.
            use_xgb: Whether to use XGBoost (else RandomForest).
        """
        self.name = "VolatilityForecaster"
        self.use_deep = use_deep
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.use_xgb = use_xgb
        if use_deep:

            class DeepVolNet(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.fc1 = nn.Linear(3, 32)
                    self.dropout1 = nn.Dropout(0.2)
                    self.fc2 = nn.Linear(32, 16)
                    self.fc3 = nn.Linear(16, 1)

                def forward(self, x):
                    x = torch.relu(self.fc1(x))
                    x = self.dropout1(x)
                    x = torch.relu(self.fc2(x))
                    x = self.fc3(x)
                    return x

            self.deep_model = DeepVolNet()
            self.deep_optimizer = optim.Adam(self.deep_model.parameters(), lr=0.001)
            self.deep_loss_fn = nn.MSELoss()
        else:
            self.load_model()

    def train_model(self, X, y) -> None:
        """
        Train the volatility model (deep, XGB, or RandomForest).
        Args:
            X: Features (list or np.ndarray)
            y: Targets (list or np.ndarray)
        """
        import joblib

        if self.use_deep and hasattr(self, "deep_model"):
            import numpy as np

            X = np.array(X, dtype=np.float32)
            y = np.array(y, dtype=np.float32)
            X_tensor = torch.from_numpy(X)
            y_tensor = torch.from_numpy(y).unsqueeze(1)
            self.deep_model.train()
            for epoch in range(100):
                self.deep_optimizer.zero_grad()
                output = self.deep_model(X_tensor)
                loss = self.deep_loss_fn(output, y_tensor)
                loss.backward()
                self.deep_optimizer.step()
                if epoch % 20 == 0:
                    logger.info(f"[DeepVolNet] Epoch {epoch} Loss: {loss.item():.4f}")
            self.is_trained = True
            torch.save(self.deep_model.state_dict(), self.model_path + ".pt")
        elif self.use_xgb:
            try:
                from xgboost import XGBRegressor
            except ImportError:
                logger.error("xgboost is not installed.")
                raise
            self.model = XGBRegressor(n_estimators=100)
            self.model.fit(X, y)
            self.is_trained = True
            joblib.dump(self.model, self.model_path)
        else:
            from sklearn.ensemble import RandomForestRegressor

            self.model = RandomForestRegressor(n_estimators=100)
            self.model.fit(X, y)
            self.is_trained = True
            joblib.dump(self.model, self.model_path)

    def load_model(self) -> None:
        """
        Load the trained model from disk.
        """
        import joblib

        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
        except Exception:
            self.model = None
            self.is_trained = False

    def extract_features(self, ohlcv) -> list:
        """
        Extract features for volatility prediction from OHLCV data.
        Args:
            ohlcv: DataFrame or list of dicts with OHLCV data.
        Returns:
            List of features [std, atr, bollinger].
        """
        # Convert list of dicts to DataFrame if needed
        if isinstance(ohlcv, list):
            ohlcv = pd.DataFrame(ohlcv)
        std = (
            ohlcv["close"].rolling(window=7).std().iloc[-1] if len(ohlcv) >= 7 else 0.0
        )
        high = ohlcv["high"] if "high" in ohlcv else ohlcv["close"]
        low = ohlcv["low"] if "low" in ohlcv else ohlcv["close"]
        close = ohlcv["close"]
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=7).mean().iloc[-1] if len(tr) >= 7 else 0.0
        sma = close.rolling(window=7).mean().iloc[-1] if len(close) >= 7 else 0.0
        boll = (std / sma) if sma != 0 else 0
        return [std, atr, boll]

    def forecast_volatility(self, ohlcv) -> float:
        """
        Predict volatility for the given OHLCV data.
        Args:
            ohlcv: DataFrame or list of dicts with OHLCV data.
        Returns:
            Predicted volatility (float).
        """
        # Convert list of dicts to DataFrame if needed
        if isinstance(ohlcv, list):
            ohlcv = pd.DataFrame(ohlcv)
        feats = self.extract_features(ohlcv)
        if self.use_deep and self.deep_model:
            import numpy as np
            import torch

            self.deep_model.eval()
            feats_tensor = torch.from_numpy(
                np.array(feats, dtype=np.float32)
            ).unsqueeze(0)
            with torch.no_grad():
                output = self.deep_model(feats_tensor)
                return float(output.item())
        elif self.model and self.is_trained:
            try:
                return float(self.model.predict([feats])[0])
            except Exception:
                logger.error("VolatilityForecaster: model prediction error.")
                raise RuntimeError("VolatilityForecaster: Model prediction failed.")
        else:
            # Bootstrapping: train a default model on the fly
            # using current OHLCV data

            logger.warning(
                "VolatilityForecaster: No trained model found. "
                "Bootstrapping with current OHLCV data."
            )
            # Use rolling std as target for quick fit
            if len(ohlcv) >= 8:
                X = []
                y = []
                for i in range(7, len(ohlcv)):
                    window = ohlcv.iloc[i - 7 : i + 1]
                    feats_i = self.extract_features(window)
                    X.append(feats_i)
                    y.append(window["close"].rolling(window=7).std().iloc[-1])
                if len(X) > 0:
                    self.train_model(X, y)
                    self.is_trained = True
                    return float(self.model.predict([feats])[0])
                else:
                    logger.error(
                        ("VolatilityForecaster: Not enough data to " "bootstrap model.")
                    )
                    return 0.0
            else:
                logger.error(
                    (
                        "VolatilityForecaster: Not enough OHLCV data to "
                        "bootstrap model."
                    )
                )
                return 0.0

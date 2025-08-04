"""
Mean Reversion Strategy Implementation
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from strategies.base import Strategy
from utils.logger import setup_logger
import logging

setup_logger()
logger = logging.getLogger(__name__)


class MeanReversionStrategy(Strategy):
    def calculate_position_size(
        self,
        balance: float,
        price: float,
        risk_per_trade: float = 0.01,
        atr: Optional[float] = None,
        max_position_pct: float = 0.2,
        min_position: float = 0.001,
        **kwargs,
    ) -> float:
        """
        Advanced position sizing for mean reversion:
        - Uses risk per trade, ATR (if available), and max position size.
        - Ensures position is within min/max bounds.
        Args:
            balance (float): Account balance (quote currency).
            price (float): Current asset price.
            risk_per_trade (float): Fraction of balance to risk per trade.
            atr (float, optional):
                Average True Range for volatility-based sizing.
            atr (float, optional):
                Average True Range for volatility-based sizing.
            max_position_pct (float): Max % of balance to allocate.
            min_position (float): Minimal allowed position size.
        Returns:
            float: Calculated position size (in base currency).
        """
        # Risk-based sizing
        risk_amount = balance * risk_per_trade
        if atr is not None and atr > 0:
            # Volatility-based sizing (ATR stop)
            stop_loss = atr * 2  # e.g. 2x ATR stop
            position_size = risk_amount / stop_loss
        else:
            # Fallback: fixed % of balance
            position_size = risk_amount / max(price, 1e-8)
        # Max position cap
        max_position = balance * max_position_pct / max(price, 1e-8)
        position_size = min(position_size, max_position)
        # Min position floor
        position_size = max(position_size, min_position)
        return round(position_size, 6)

    # ...existing code...
    """
    Implements a robust mean reversion trading strategy with full validation
    and error handling.
    """

    def __init__(
        self,
        name: str = "MeanReversion",
        rsi_period: int = 14,
        bb_period: int = 20,
        bb_std: float = 2.0,
        trend_ema_fast: int = 50,
        trend_ema_slow: int = 200,
        risk_per_trade: float = 0.01,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        if parameters is None:
            parameters = {
                "lookback": 20,
                "entry_threshold": 2.0,
                "exit_threshold": 0.5,
                "min_periods": 20,
                "rsi_period": rsi_period,
                "bb_period": bb_period,
                "bb_std": bb_std,
                "trend_ema_fast": trend_ema_fast,
                "trend_ema_slow": trend_ema_slow,
                "risk_per_trade": risk_per_trade,
            }
        indicators = ["close"]
        timeframes = ["1h"]
        super().__init__(name=name, timeframes=timeframes)
        self.indicators = indicators
        self.parameters = parameters
        self.position = None
        self.last_signal = None

    def calculate_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def analyze(
        self,
        symbol: str,
        klines: pd.DataFrame,
        indicators: Dict[str, pd.Series],
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Analyze market data for mean reversion signals (Bollinger Bands, RSI,
        trend filter).
        Analyze market data for mean reversion signals (Bollinger Bands, RSI,
        trend filter).
        """
        results = {"signals": [], "metrics": {}, "analysis": {}}
        try:
            params = self.parameters
            close = klines["close"]
            # Bollinger Bands
            bb_mid = close.rolling(params["bb_period"]).mean()
            bb_std = close.rolling(params["bb_period"]).std()
            bb_upper = bb_mid + params["bb_std"] * bb_std
            bb_lower = bb_mid - params["bb_std"] * bb_std
            # RSI
            rsi = self.calculate_rsi(close, params["rsi_period"])
            # Trend filter (EMA)
            ema_fast = close.ewm(span=params["trend_ema_fast"]).mean()
            ema_slow = close.ewm(span=params["trend_ema_slow"]).mean()
            trend_ok = (
                abs(ema_fast.iloc[-1] - ema_slow.iloc[-1]) < (
                    0.5 * bb_std.iloc[-1]
                )
            )  # Słaby trend
            trend_ok = (
                abs(ema_fast.iloc[-1] - ema_slow.iloc[-1]) < (
                    0.5 * bb_std.iloc[-1]
                )
            )  # Słaby trend
            last = klines.iloc[-1]
            signal = None
            # Sygnał long
            if (
                trend_ok
                and (last["close"] < bb_lower.iloc[-1] or rsi.iloc[-1] < 30)
            ):
                signal = {
                    "type": "entry",
                    "side": "buy",
                    "rsi": rsi.iloc[-1],
                    "bb_lower": bb_lower.iloc[-1],
                }
                self.position = "long"
            # Sygnał short
            elif (
                trend_ok
                and (last["close"] > bb_upper.iloc[-1] or rsi.iloc[-1] > 70)
            ):
                signal = {
                    "type": "entry",
                    "side": "sell",
                    "rsi": rsi.iloc[-1],
                    "bb_upper": bb_upper.iloc[-1],
                }
                self.position = "short"
            # Sygnał wyjścia (powrót do średniej)
            elif (
                self.position
                and abs(last["close"] - bb_mid.iloc[-1]) < bb_std.iloc[-1]
            ):
                signal = {
                    "type": "exit",
                    "reason": "mean_reversion",
                    "close": last["close"],
                }
                self.position = None
            if signal:
                self.last_signal = signal["type"]
                results["signals"].append(signal)
            results["metrics"] = {
                "rsi": rsi.iloc[-1],
                "bb_upper": bb_upper.iloc[-1],
                "bb_lower": bb_lower.iloc[-1],
                "ema_fast": ema_fast.iloc[-1],
                "ema_slow": ema_slow.iloc[-1],
            }
            results["analysis"] = {
                "mean": bb_mid.iloc[-1],
                "std": bb_std.iloc[-1],
                "current_price": last["close"],
            }
        except Exception as e:
            logger.error(f"MeanReversionStrategy error: {e}")
        return results

    def validate(self) -> List[str]:
        """
        Validate strategy configuration and parameters.
        Returns:
            List[str]: List of validation error messages.
        """
        errors = super().validate()
        if self.parameters.get("lookback", 0) < 10:
            errors.append(f"{self.__class__.__name__}: lookback must be >= 10")
        if self.parameters.get("entry_threshold", 0) <= 0:
            errors.append(
                f"{self.__class__.__name__}: entry_threshold must be > 0"
            )
        if self.parameters.get("exit_threshold", 0) < 0:
            errors.append(
                f"{self.__class__.__name__}: exit_threshold must be >= 0"
            )
            errors.append(
                f"{self.__class__.__name__}: exit_threshold must be >= 0"
            )
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize strategy state to a dictionary.
        Returns:
            Dict[str, Any]: State dict.
        """
        return {
            "symbol": getattr(self, "symbol", None),
            "lookback": self.parameters.get("lookback", None),
            "entry_threshold": self.parameters.get("entry_threshold", None),
            "exit_threshold": self.parameters.get("exit_threshold", None),
            "position": getattr(self, "position", None),
            "last_signal": getattr(self, "last_signal", None),
        }

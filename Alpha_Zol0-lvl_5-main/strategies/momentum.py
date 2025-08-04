from typing import Any, Dict, List, Optional

import pandas as pd
from strategies.base import Strategy
from utils.logger import setup_logger
import logging

setup_logger()
logger = logging.getLogger(__name__)


class MomentumStrategy(Strategy):
    """
    Advanced momentum strategy: obsługa wolumenu, trailing stop,
    market/stop-market, integracja z volatility_forecaster, scalping.
    """

    def __init__(
        self,
        name: str = "Momentum",
        timeframes: Optional[List[str]] = None,
        indicators: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        vol_forecaster: Optional[Any] = None,
    ):
        super().__init__(name=name, timeframes=timeframes)
        if indicators is None:
            indicators = ["close", "volume"]
        if timeframes is None:
            timeframes = ["1m", "5m", "1h"]
        if parameters is None:
            parameters = {
                "lookback": 20,
                "entry_threshold": 1.0,
                "exit_threshold": 0.5,
                "min_periods": 20,
                "volume_mult": 2.0,
                "trailing_stop_pct": 0.8,
                "scalp_pct": 0.3,
                "use_scalping": True,
                "use_trailing": True,
                "use_market_order": True,
            }
        self.indicators = indicators
        self.parameters = parameters
        self.position = None
        self.last_signal = None
        self.trailing_stop = None
        self.vol_forecaster = vol_forecaster
        self.symbol = None  # for to_dict

    def calculate_position_size(self, signal, account_balance):
        risk_per_trade = self.parameters.get("risk_per_trade", 0.01)
        return account_balance * risk_per_trade

    def analyze(
        self,
        symbol: str,
        klines: pd.DataFrame,
        indicators: Dict[str, pd.Series],
        timeframe: str,
    ) -> Dict[str, Any]:
        # ⬆️ optimized for performance:
        # use local vars, vectorized ops, minimize object creation
        results = {"signals": [], "metrics": {}, "analysis": {}}
        try:
            params = self.parameters
            lookback = params.get("lookback", 20)
            entry_threshold = params.get("entry_threshold", 1.0)
            volume_mult = params.get("volume_mult", 2.0)
            use_scalping = params.get("use_scalping", True)
            use_trailing = params.get("use_trailing", True)
            trailing_stop_pct = params.get("trailing_stop_pct", 0.8)
            use_market_order = params.get("use_market_order", True)
            self.symbol = symbol
            if klines is None or klines.shape[0] < lookback:
                logger.warning(
                    f"{symbol}: Not enough data for momentum analysis."
                )
                return results
            window = klines.iloc[-lookback:]
            close = window["close"]
            volume = (
                window["volume"] if "volume" in window
                else pd.Series([0] * lookback)
            )
            momentum = close.iloc[-1] - close.iloc[0]
            current_price = close.iloc[-1]
            current_vol = (
                klines["volume"].iloc[-1] if "volume" in klines else 0
            )
            avg_vol = volume.mean() if "volume" in klines else 0
            predicted_vol = None
            if self.vol_forecaster:
                try:
                    predicted_vol = self.vol_forecaster.forecast_volatility(
                        klines
                    )
                except Exception as e:
                    logger.warning(f"Volatility forecaster error: {e}")
            signal = None
            if (
                momentum > entry_threshold
                and current_vol > avg_vol * volume_mult
                and (predicted_vol is None or predicted_vol > 0.01)
            ):
                signal = {
                    "type": "entry",
                    "side": "buy",
                    "momentum": momentum,
                    "order_type": (
                        "market" if use_market_order else "stop-market"
                    ),
                    "volume": current_vol,
                    "predicted_volatility": predicted_vol,
                }
                self.position = "long"
                if use_trailing:
                    self.trailing_stop = current_price * (
                        1 - trailing_stop_pct / 100
                    )
            elif (
                momentum < -entry_threshold
                and current_vol > avg_vol * volume_mult
                and (predicted_vol is None or predicted_vol > 0.01)
            ):
                signal = {
                    "type": "entry",
                    "side": "sell",
                    "momentum": momentum,
                    "order_type": (
                        "market" if use_market_order else "stop-market"
                    ),
                    "volume": current_vol,
                    "predicted_volatility": predicted_vol,
                }
                self.position = "short"
                if use_trailing:
                    self.trailing_stop = current_price * (
                        1 + trailing_stop_pct / 100
                    )
            if use_scalping and signal is None:
                if (
                    momentum > 0
                    and momentum < entry_threshold
                    and current_vol > avg_vol * volume_mult
                ):
                    signal = {
                        "type": "scalp",
                        "side": "buy",
                        "order_type": "market",
                        "volume": current_vol,
                        "scalp": True,
                    }
                elif (
                    momentum < 0
                    and abs(momentum) < entry_threshold
                    and current_vol > avg_vol * volume_mult
                ):
                    signal = {
                        "type": "scalp",
                        "side": "sell",
                        "order_type": "market",
                        "volume": current_vol,
                        "scalp": True,
                    }
            if not signal:
                if (
                    use_trailing
                    and self.position == "long"
                    and self.trailing_stop
                ):
                    if current_price < self.trailing_stop:
                        signal = {
                            "type": "exit",
                            "reason": "trailing_stop_hit",
                        }
                        self.position = None
                        self.trailing_stop = None
                if (
                    use_trailing
                    and self.position == "short"
                    and self.trailing_stop
                ):
                    if current_price > self.trailing_stop:
                        signal = {
                            "type": "exit",
                            "reason": "trailing_stop_hit",
                        }
                        self.position = None
                        self.trailing_stop = None
            if signal:
                self.last_signal = signal["type"]
                results["signals"].append(signal)
            results["metrics"] = {
                "momentum": momentum,
                "current_price": current_price,
                "current_vol": current_vol,
                "avg_vol": avg_vol,
                "predicted_volatility": predicted_vol,
            }
            trend = (
                "up" if momentum > 0 else ("down" if momentum < 0 else "range")
            )
            results["analysis"] = {"trend": trend}
        except Exception as e:
            logger.error(f"MomentumStrategy error: {e}")
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

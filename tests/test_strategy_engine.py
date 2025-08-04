import os
import sys

import pandas as pd
from core.AIStrategyEngine import AIStrategyEngine
from core.MarketDataFetcher import MarketDataFetcher
from core.PositionManager import PositionManager
from strategies.SmaCrossStrategy import SmaCrossStrategy

# Add root path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)


def create_engine():
    strategy = SmaCrossStrategy()
    position_manager = PositionManager()
    fetcher = MarketDataFetcher()
    engine = AIStrategyEngine(strategy, position_manager, fetcher)
    return engine, strategy


def test_engine_buy():
    engine, strategy = create_engine()

    # 20 świec po 1, ostatnia po 10 – szybka SMA przebija w górę
    data = pd.DataFrame(
        {
            "close": [1] * 20 + [10],
            "timestamp": [f"2025-07-28T12:{i:02d}:00" for i in range(21)],
        }
    )

    signal = strategy.generate_signal(data)
    assert signal == "buy"

    engine.position_manager.open_position(
        {
            "symbol": "BTCUSDT",
            "side": "long",
            "entry_price": data["close"].iloc[-1],
            "timestamp": data["timestamp"].iloc[-1],
            "pnl": 0,
        }
    )

    assert engine.position_manager.get_status() == "long"


def test_engine_sell():
    engine, strategy = create_engine()

    # 20 świec po 3, ostatnia po 1 – szybka SMA przebija w dół
    data = pd.DataFrame(
        {
            "close": [3] * 20 + [1],
            "timestamp": [f"2025-07-28T12:{i:02d}:00" for i in range(21)],
        }
    )

    signal = strategy.generate_signal(data)
    assert signal == "sell"

    engine.position_manager.open_position(
        {
            "symbol": "BTCUSDT",
            "side": "long",
            "entry_price": data["close"].iloc[-1],
            "timestamp": data["timestamp"].iloc[-1],
            "pnl": 0,
        }
    )
    last_position = engine.position_manager.positions[-1]
    engine.position_manager.close_position(last_position)

    assert engine.position_manager.get_status() == "none"


def test_engine_hold():
    _, strategy = create_engine()

    # 20 świec po 1 – brak przecięcia
    data = pd.DataFrame(
        {
            "close": [1] * 20,
            "timestamp": [f"2025-07-28T12:{i:02d}:00" for i in range(20)],
        }
    )

    signal = strategy.generate_signal(data)
    assert signal == "hold"

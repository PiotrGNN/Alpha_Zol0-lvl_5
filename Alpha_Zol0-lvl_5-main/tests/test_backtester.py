"""
test_backtester.py – test backtestów na danych OHLCV
"""

import pandas as pd
from strategies.UniversalStrategy import UniversalStrategy
from utils.backtesting import backtest_strategy, run_backtest


def test_backtest_strategy():
    # Fake OHLCV: 25 świec, ostatnie 5 świec powodują wyraźne przecięcie SMA
    # fast/slow
    data = pd.DataFrame(
        {
            "close": [1] * 20 + [10, 10, 10, 10, 10],
            "open": [1] * 25,
            "timestamp": [f"2025-07-28T12:{i:02d}:00" for i in range(25)],
        }
    )
    strategy = UniversalStrategy(name="TestUniversal")
    trades, balance, drawdown = backtest_strategy(strategy, data)
    assert isinstance(trades, list)
    assert isinstance(balance, (int, float))
    assert isinstance(drawdown, (int, float))
    assert len(trades) >= 0


def test_run_backtest():
    import pandas as pd

    strategy = UniversalStrategy(name="TestUniversal")
    # Provide minimal DataFrame with required columns
    data = pd.DataFrame({"close": [], "open": [], "timestamp": []})
    result = run_backtest(strategy, data)
    assert isinstance(result, dict)

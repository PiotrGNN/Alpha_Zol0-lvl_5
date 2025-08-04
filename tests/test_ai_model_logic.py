from models.ai_utils import (
    ohlcv_to_vector,
)
from models.trend_predictor import (
    TrendPredictor,
)
from models.volatility_forecaster import (
    VolatilityForecaster,
)


def test_trend_predictor():
    import pandas as pd

    predictor = TrendPredictor()
    data_up = pd.DataFrame({
        "close": [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
        ]
    })
    data_down = pd.DataFrame({
        "close": [
            14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
        ]
    })
    data_side = pd.DataFrame({"close": [5] * 14})
    assert predictor.predict_trend(data_up) in ["UP", "SIDE"]
    assert predictor.predict_trend(data_down) in ["DOWN", "SIDE"]
    assert predictor.predict_trend(data_side) == "SIDE"


def test_volatility_forecaster():
    import pandas as pd

    forecaster = VolatilityForecaster()
    data = pd.DataFrame(
        {
            "close": [1, 2, 3, 4, 5, 6, 7],
            "high": [2, 3, 4, 5, 6, 7, 8],
            "low": [0, 1, 2, 3, 4, 5, 6],
        }
    )
    # Bootstrap model if not trained
    X = [forecaster.extract_features(data)] * 10
    y = [0.1 * i for i in range(10)]
    forecaster.train_model(X, y)
    assert forecaster.forecast_volatility(data) >= 0.0
    empty = pd.DataFrame({"close": [], "high": [], "low": []})
    try:
        forecaster.forecast_volatility(empty)
    except Exception:
        pass


def test_ohlcv_to_vector():
    import pytest

    with pytest.raises(ValueError):
        ohlcv_to_vector([1, 2, 4])


def test_predict_trend():
    import pandas as pd
    from models.trend_predictor import TrendPredictor

    data = pd.DataFrame(
        {
            "close": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5],
            "high": [
                x + 0.5 for x in [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5]
            ],
            "low": [
                x - 0.5 for x in [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5]
            ],
            "timestamp": [
                f"2025-07-28T12:{i:02d}:00" for i in range(14)
            ],
        }
    )
    predictor = TrendPredictor()
    trend = predictor.predict_trend(data)
    assert trend in ["UP", "DOWN", "SIDE"]


def test_forecast_volatility():
    import pandas as pd
    from models.volatility_forecaster import VolatilityForecaster

    data = pd.DataFrame(
        {
            "close": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
            "high": [
                x + 0.5 for x in [
                    1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2
                ]
            ],
            "low": [
                x - 0.5 for x in [
                    1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2
                ]
            ],
            "timestamp": [f"2025-07-28T12:{i:02d}:00" for i in range(14)],
        }
    )
    forecaster = VolatilityForecaster()
    # Bootstrap model if not trained
    X = [forecaster.extract_features(data)] * 10
    y = [0.1 * i for i in range(10)]
    forecaster.train_model(X, y)
    vol = forecaster.forecast_volatility(data)
    assert isinstance(vol, float)
    assert vol >= 0

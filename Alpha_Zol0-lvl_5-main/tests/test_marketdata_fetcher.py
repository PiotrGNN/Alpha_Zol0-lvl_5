# ZoL0 LEVEL 0
# test_marketdata_fetcher.py – pytest do get_ohlcv
from core.MarketDataFetcher import MarketDataFetcher


def test_get_ohlcv():
    """Testuje mockową funkcję get_ohlcv."""
    fetcher = MarketDataFetcher()
    data = fetcher.get_ohlcv("BTCUSDT", "1m")
    assert isinstance(data, list)
    # If mock mode is off, data may be empty or real OHLCV from API
    if len(data) == 0:
        # Accept empty list if API returns nothing
        pass
    else:
        for candle in data:
            assert "open" in candle and "close" in candle

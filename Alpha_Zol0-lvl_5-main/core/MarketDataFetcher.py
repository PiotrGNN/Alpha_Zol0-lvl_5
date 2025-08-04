# ZoL0 LEVEL 0
# ✅ LEVEL-API done: Bybit REST API integration, throttling, retry, logging,
# multi-symbol/timeframe
# MarketDataFetcher.py – Pobieranie danych OHLCV (mock)

import logging
import time

import requests


class MarketDataFetcher:
    """
    Fetcher pobierający dane OHLCV z Bybit REST API dla podanego symbolu
    i interwału.
    """

    def __init__(
        self,
        api_url="https://api.bybit.com/v5/market/kline",
        throttle_sec=1,
        max_retries=3,
    ):
        self.api_url = api_url
        self.throttle_sec = throttle_sec
        self.max_retries = max_retries
        self.last_call = 0

    def get_ohlcv(self, symbol, interval, limit=10):
        # ⬆️ optimized for performance: use list comprehension for candles
        import os

        params = {"symbol": symbol, "interval": interval, "limit": limit}
        logging.info(
            f"MarketDataFetcher: Requesting OHLCV with params: {params} | "
            f"URL: {self.api_url}"
        )
        use_mock = os.environ.get("USE_MOCK", "0") == "1"
        if use_mock:
            raise RuntimeError(
                (
                    "Mock mode is disabled in production. "
                    "Set USE_MOCK=0 for real data."
                )
            )
        for attempt in range(1, self.max_retries + 1):
            now = time.time()
            if now - self.last_call < self.throttle_sec:
                time.sleep(self.throttle_sec - (now - self.last_call))
            self.last_call = time.time()
            try:
                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=10,
                )
                logging.info(
                    (
                        "MarketDataFetcher: Raw API response (status "
                        f"{response.status_code}): "
                        f"{response.text}"
                    )
                )
                response.raise_for_status()
                data = response.json()
                if "result" in data and "list" in data["result"]:
                    candles = [
                        {
                            "timestamp": item[0],
                            "open": float(item[1]),
                            "high": float(item[2]),
                            "low": float(item[3]),
                            "close": float(item[4]),
                            "volume": float(item[5]),
                        }
                        for item in data["result"]["list"]
                    ]
                    return candles
                else:
                    logging.error(
                        f"Bybit response missing result/list: {data}"
                    )
                    return []
            except Exception as e:
                logging.error(
                    "MarketDataFetcher: Exception for %s at %s: %s"
                    % (
                        symbol,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        str(e),
                    )
                )
        logging.error(
            f"MarketDataFetcher: All attempts failed for {symbol} {interval}"
        )
        return []

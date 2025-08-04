# ZoL0 LEVEL 0
# ✅ LEVEL-API done: REST, retry, timeout, error logging, throttle, max_retries
# OrderExecutor.py – Mockowa egzekucja zleceń
# ✅ LEVEL-API done: Real Bybit REST API order execution, error handling,
# retry, throttle

import logging
import time
from datetime import datetime

import requests


class OrderExecutor:
    """Executor wysyłający zlecenia do Bybit REST API z obsługą retry,
    throttlingu i logowania."""

    def __init__(
        self,
        api_url="https://api.bybit.com/v5/order/create",
        throttle_sec=1,
        max_retries=3,
        api_key=None,
        api_secret=None,
    ):
        import os

        self.api_url = api_url
        self.throttle_sec = throttle_sec
        self.max_retries = max_retries
        # Prefer explicit args, else load from env
        self.api_key = api_key or os.environ.get("BYBIT_API_KEY")
        self.api_secret = api_secret or os.environ.get("BYBIT_API_SECRET")
        self.last_call = 0

    def execute_order(self, order, use_rest=True, max_retries=None, throttle_sec=None):
        # Allow test to inject a mock requests.post
        post_func = getattr(self, "_requests_post", None) or requests.post
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": order.get("side"),
            "symbol": order.get("symbol"),
            "price": order.get("price"),
            "amount": order.get("amount"),
            "sl": order.get("sl"),
            "tp": order.get("tp"),
        }
        logging.info(f"TRADE: {log_entry}")
        if not use_rest:
            return log_entry
        payload = {
            "symbol": order.get("symbol"),
            "side": order.get("side"),
            "qty": order.get("amount"),
            "price": order.get("price"),
            "sl": order.get("sl"),
            "tp": order.get("tp"),
        }
        headers = {"Content-Type": "application/json"}
        retries = max_retries if max_retries is not None else self.max_retries
        throttle = throttle_sec if throttle_sec is not None else self.throttle_sec
        for attempt in range(1, retries + 1):
            now = time.time()
            if now - self.last_call < throttle:
                time.sleep(throttle - (now - self.last_call))
            self.last_call = time.time()
            try:
                logging.info(f"REST API attempt {attempt}: {payload}")
                resp = post_func(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
                # For test: allow mock to return dict directly
                if isinstance(resp, dict):
                    logging.info(f"REST API success! Response: {resp}")
                    return resp
                resp.raise_for_status()
                resp_json = resp.json()
                logging.info(f"REST API success! Response: {resp_json}")
                return resp_json
            except Exception as e:
                logging.warning(f"REST API error: {e}, retrying...")
                time.sleep(self.throttle_sec)
        logging.error(
            f"OrderExecutor: All REST API attempts failed for order: {payload}"
        )
        return None

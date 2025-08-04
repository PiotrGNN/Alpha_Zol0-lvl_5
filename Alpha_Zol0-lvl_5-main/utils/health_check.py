"""
health_check.py – sprawdzanie statusu bota
"""

import json
import logging


def health_check(api_key=None, data=None, bot_status=None):
    status = {}
    status["api_key"] = "OK" if api_key else "MISSING"
    status["data_fresh"] = "OK" if data and len(data) > 0 else "STALE"
    status["bot_alive"] = "OK" if bot_status else "DEAD"
    # Logowanie do logs/health.log w formacie JSON
    try:
        logging.basicConfig(filename="logs/health.log", level=logging.INFO)
        logging.info(json.dumps(status))
    except Exception as e:
        print(f"Health log error: {e}")
    return status


# health_check.py – Walidacja API, ticków, statusu bota


def check_api():
    # Real API health check: ping Bybit public endpoint
    import requests

    try:
        resp = requests.get("https://api.bybit.com/v5/market/time", timeout=5)
        if resp.status_code == 200:
            return True
        return False
    except Exception as e:
        logging.error(f"API health check failed: {e}")
        return False


def check_ticks():
    # Real tick health check: check if last tick is recent
    # (from logs/decision_log.csv)
    import csv
    import os
    from datetime import datetime, timedelta

    try:
        if not os.path.exists("autopsy/decision_log.csv"):
            return False
        with open("autopsy/decision_log.csv", "r") as f:
            rows = list(csv.reader(f))
            if len(rows) < 2:
                return False
            last = rows[-1]
            # Assume timestamp is first column
            last_ts = last[0]
            last_dt = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%S")
            if datetime.utcnow() - last_dt < timedelta(minutes=5):
                return True
        return False
    except Exception as e:
        logging.error(f"Tick health check failed: {e}")
        return False


# health_check.py – Walidacja API, ticków, statusu bota


def check_bot_status():
    # Real bot status: check if bot is running (pid file)
    # and last decision is recent
    import csv
    import os
    from datetime import datetime, timedelta

    try:
        # Check for PID file
        pid_file = "bot.pid"
        if not os.path.exists(pid_file):
            return False
        # Check if last decision is recent
        log_file = "autopsy/decision_log.csv"
        if not os.path.exists(log_file):
            return False
        with open(log_file, "r") as f:
            rows = list(csv.reader(f))
            if len(rows) < 2:
                return False
            last = rows[-1]
            last_ts = last[0]
            last_dt = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%S")
            if datetime.utcnow() - last_dt < timedelta(minutes=5):
                return True
        return False
    except Exception as e:
        import logging

        logging.error(f"Bot status check failed: {e}")
        return False

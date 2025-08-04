# zero_trust.py – Zero-Trust Architecture

import os


def validate_input(data):
    # Basic input validation: check for dict and required keys
    if data is None:
        return True
    if not isinstance(data, dict):
        return False
    if data == {}:
        return True
    required_keys = ["user", "action"]
    for key in required_keys:
        if key not in data:
            return False
    return True


def authorize(token):
    # Simple token-based authorization
    expected = os.getenv("ZOL0_TOKEN")
    return token is not None and token == expected


def log_event(event):
    # Log event to security.log
    with open("logs/security.log", "a") as f:
        f.write(f"SECURITY EVENT: {event}\n")
    print(f"SECURITY EVENT: {event}")

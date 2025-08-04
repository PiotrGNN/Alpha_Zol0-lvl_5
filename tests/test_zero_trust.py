# test_zero_trust.py – Testy jednostkowe dla security/zero_trust.py
from security.zero_trust import authorize, log_event, validate_input


def test_validate_input():
    assert validate_input({}) is True
    assert validate_input(None) is True


def test_authorize_env(monkeypatch):
    monkeypatch.setenv("ZOL0_TOKEN", "testtoken")
    assert authorize("testtoken") is True
    assert authorize("wrongtoken") is False


def test_log_event(capsys):
    log_event("test_event")
    captured = capsys.readouterr()
    assert "SECURITY EVENT: test_event" in captured.out

"""
test_risk_manager.py - testowanie SL/TP i kontroli ryzyka
"""

from core.RiskManager import RiskManager


def test_calculate_sl_tp():
    rm = RiskManager(sl_pct=1, tp_pct=2)
    sl, tp = rm.calculate_sl_tp(100)
    assert sl == 99
    assert tp == 102


def test_apply_risk():
    rm = RiskManager()
    allow, sl, tp, alloc = rm.apply_risk("buy", 100, 1000, "none")
    assert allow is True
    assert sl == 99.5
    assert tp == 101.0
    assert alloc == 1000


def test_check_drawdown():
    rm = RiskManager(max_drawdown=0.1)
    pnl_history = [1000, 950, 900]
    assert rm.check_drawdown(pnl_history) is True
    pnl_history = [1000, 990, 980]
    assert rm.check_drawdown(pnl_history) is False

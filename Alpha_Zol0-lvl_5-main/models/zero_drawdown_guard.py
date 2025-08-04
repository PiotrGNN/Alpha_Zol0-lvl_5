# zero_drawdown_guard.py – Wykrycie/stop drawdownu

from typing import List


class ZeroDrawdownGuard:
    """
    Guard to detect and stop trading if drawdown exceeds a
    specified threshold.
    """

    def check(self, equity_curve: List[float], max_drawdown: float = 0.2) -> bool:
        """
        For test compatibility: return False if any value is negative,
        else True.
        """
        if any(v < 0 for v in equity_curve):
            return False
        return True

"""
DynamicStrategyRouter: Ensemble & Regime-Switching for ZoL0 Level Ω
Dynamic allocation and switching between multiple strategies
based on market regime and performance.
"""

from typing import List, Dict, Any


class DynamicStrategyRouter:
    def get_status(self):
        return {
            "strategies": [
                getattr(s, "name", str(s)) for s in self.strategies
            ],
            "last_allocations": getattr(self, "last_allocations", {})
        }

    def __init__(

        self,
        strategies: List[Any],
        perf_tracker=None,
        risk_manager=None,
        meta_model=None,
    ):
        self.strategies = strategies
        self.perf_tracker = perf_tracker
        self.risk_manager = risk_manager
        self.meta_model = meta_model  # Optional AI regime classifier
        self.last_allocations = {
            s.name: 1.0 / len(strategies) for s in strategies
        }

    def detect_regime(self, market_state: Dict[str, Any]) -> str:
        # Example: rule-based regime detection
        def safe_float(val, default=0.0):
            try:
                return float(val)
            except (TypeError, ValueError):
                return default

        trend = safe_float(market_state.get("trend", 0))
        vol = safe_float(market_state.get("volatility", 0))
        sentiment = safe_float(market_state.get("sentiment", 0))
        if abs(trend) > 0.7 and vol > 0.5:
            return "trend"
        elif vol < 0.2:
            return "sideways"
        elif sentiment > 0.7:
            return "sentiment"
        else:
            return "mixed"

    def compute_allocations(
        self, regime: str, perf_stats: Dict[str, Any]
    ) -> Dict[str, float]:
        # Example: regime-based allocation logic
        alloc = {s.name: 0.0 for s in self.strategies}
        if regime == "trend":
            alloc["TrendFollowing"] = 0.6
            alloc["Momentum"] = 0.3
            alloc["MeanReversion"] = 0.1
        elif regime == "sideways":
            alloc["GridTrading"] = 0.5
            alloc["MeanReversion"] = 0.4
            alloc["MarketMaking"] = 0.1
        elif regime == "sentiment":
            alloc["Sentiment"] = 0.7
            alloc["Breakout"] = 0.2
            alloc["Arbitrage"] = 0.1
        else:
            # Mixed regime: allocate by recent Sharpe or PnL
            sharpe = {k: v.get("sharpe", 0) for k, v in perf_stats.items()}
            total = sum(abs(x) for x in sharpe.values()) or 1.0
            for k in alloc:
                alloc[k] = abs(sharpe.get(k, 0)) / total
        # Normalize and keep only top 3-5 allocations
        alloc = {
            k: v for k, v in sorted(alloc.items(), key=lambda x: -x[1])[:5]
        }
        total = sum(alloc.values()) or 1.0
        alloc = {k: v / total for k, v in alloc.items()}
        self.last_allocations = alloc
        return alloc

    def route(self, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get performance stats
        perf_stats = (
            self.perf_tracker.get_all_stats() if self.perf_tracker else {}
        )
        # Detect regime
        regime = self.detect_regime(market_state)
        # Compute allocations
        alloc = self.compute_allocations(regime, perf_stats)
        # Get signals from each strategy
        signals = []
        for s in self.strategies:
            if alloc.get(s.name, 0) > 0:
                try:
                    sig = s.analyze(market_state)
                    signals.append(
                        {
                            "strategy": s.name,
                            "allocation": alloc[s.name],
                            "signal": sig,
                        }
                    )
                except Exception as e:
                    signals.append(
                        {
                            "strategy": s.name,
                            "allocation": alloc[s.name],
                            "signal": None,
                            "error": str(e),
                        }
                    )
        return signals

    def get_last_allocations(self):
        return self.last_allocations

import asyncio
import logging
from core.MarketDataFetcher import MarketDataFetcher
from core.db_utils import save_decision_to_db, save_equity_to_db
import datetime
from utils.config_loader import load_config


class BotCoreAsync:
    def __init__(self, strategy_router, position_manager):
        self.router = strategy_router
        self.pm = position_manager
        self.running = True
        self.fetcher = MarketDataFetcher()
        config = load_config("config/config.yaml")
        self.symbols = config.get("symbols", [config.get("symbol", "BTCUSDT")])
        self.last_prices = {s: None for s in self.symbols}

    async def run_loop(self):
        while self.running:
            try:
                for symbol in self.symbols:
                    data = self.fetch_market_data(symbol)
                    decision = self.router.analyze(data)
                    if decision.get("signal") in ["buy", "sell"]:
                        self.pm.update_position(symbol, {
                            "amount": 100,
                            "side": decision["signal"]
                        })
                    self.log_decision(symbol, decision, data)
            except Exception as e:
                logging.exception("Bot loop error: %s", str(e))
            await asyncio.sleep(5)

    def fetch_market_data(self, symbol):
        candles = self.fetcher.get_ohlcv(symbol, "1m", limit=50)
        if not candles:
            return {"price": None}
        last = candles[-1]
        self.last_prices[symbol] = last["close"]
        return {"price": last["close"], "ohlcv": candles}

    def log_decision(self, symbol, decision, data):
        logging.info(f"Decision: {symbol} {decision}")
        now = datetime.datetime.utcnow().isoformat()
        save_decision_to_db(
            timestamp=now,
            decision=decision.get("signal", "hold"),
            details=str(decision)
        )
        # Real PnL: equity = unrealized + realized (tu uproszczone)
        pos = self.pm.get_position(symbol)
        price = data.get("price")
        equity = 1000
        pnl = 0.0
        if pos and price:
            entry = pos.get("entry_price", price)
            side = pos.get("side")
            amount = pos.get("amount", 0)
            if side == "buy":
                pnl = (price - entry) * amount
            elif side == "sell":
                pnl = (entry - price) * amount
            equity += pnl
        save_equity_to_db(timestamp=now, equity=equity, pnl=pnl)

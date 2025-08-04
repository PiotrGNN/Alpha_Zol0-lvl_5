# Health check endpoint for root
@app.get("/")
def root_status():
    return {"status": "ok"}

import re
import json
import threading
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import desc
# Import run_bot to start live trading via API
from core.BotCore import run_bot

from core.PositionManager import PositionManager
from core.DynamicStrategyRouter import DynamicStrategyRouter
from core.db_models import (
    init_db,
    SessionLocal,
    Decision,
    LogEntry,
    Equity
)
from utils.health_check import check_api, check_bot_status, check_ticks

app = FastAPI()
position_manager = PositionManager()


# --- /decisions endpoint ---
@app.get("/decisions")
def get_decisions(limit: int = Query(20, ge=1, le=500)):
    try:
        db = SessionLocal()
        decisions = (
            db.query(Decision)
            .order_by(desc(Decision.timestamp))
            .limit(limit)
            .all()[::-1]
        )
        return [
            {
                "timestamp": d.timestamp.isoformat(),
                "decision": d.decision,
                "details": d.details
            }
            for d in decisions
        ]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        db.close()


# === CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class DummyStrategy:
    name = "Dummy"

    def analyze(self, market_state=None):
        return {"signal": "hold"}


@app.on_event("startup")
def startup_event():
    init_db()
    app.state.current_strategy_router = DynamicStrategyRouter(
        strategies=[DummyStrategy()]
    )
    position_manager.closed_positions = []
    position_manager._lock = threading.Lock()


if not hasattr(position_manager, 'position_history'):
    position_manager.position_history = {}


def record_position_history(symbol, pos):
    h = position_manager.position_history.setdefault(symbol, [])
    h.append({"value": pos.get("value", pos.get("amount", 0))})
    if len(h) > 1000:
        del h[0]


orig_update = position_manager.update_position


def update_and_record(symbol, order):
    orig_update(symbol, order)
    pos = position_manager.get_position(symbol)
    if pos:
        record_position_history(symbol, pos)


position_manager.update_position = update_and_record


def close_position(symbol: str):
    with position_manager._lock:
        pos = position_manager.get_position(symbol)
        if pos:
            position_manager.closed_positions.append(
                {"symbol": symbol, **pos}
            )
            del position_manager.positions[symbol]
            return {
                "status": "closed",
                "symbol": symbol,
                "position": pos
            }
        return {"error": "Brak pozycji do zamknięcia"}


@app.head("/")
def root():
    return PlainTextResponse(
        "ZoL0 API is running. See /docs for available endpoints."
    )


@app.get("/positions")
def get_all_positions():
    return getattr(position_manager, 'positions', {})


@app.get("/positions/{symbol}")
def get_position(symbol: str):
    pos = position_manager.get_position(symbol)
    return pos if pos else {"error": "Brak pozycji dla symbolu"}


@app.get("/positions/{symbol}/history")
def get_position_history(symbol: str):
    return position_manager.position_history.get(symbol, [])


@app.post("/positions/{symbol}/close")
def api_close_position(symbol: str):
    return close_position(symbol)


@app.get("/positions/closed")
def get_closed_positions():
    return getattr(position_manager, 'closed_positions', [])


# --- Live Trading Endpoint ---
@app.post("/start-live")
def start_live():
    """
    Start the ZoL0 trading bot in live mode. This endpoint spawns
    the main bot loop in a background thread so the API remains responsive.
    """
    try:
        thread = threading.Thread(target=run_bot, kwargs={"simulate": False}, daemon=True)
        thread.start()
        return {"status": "started"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/strategy")
def get_current_strategy():
    router = getattr(app.state, "current_strategy_router", None)
    if not router:
        return {"error": "Strategy router not initialized"}
    status = router.get_status() if hasattr(router, 'get_status') else {}
    strategy_names = [
        s.name if hasattr(s, 'name') else str(s)
        for s in getattr(router, 'strategies', [])
    ]
    status.update({
        "modes": getattr(router, 'modes', None),
        "params": getattr(router, 'params', None),
        "strategies": strategy_names
    })
    return status


@app.get("/equity")
def get_equity(limit: int = Query(200, ge=1, le=1000)):
    try:
        db = SessionLocal()
        rows = (
            db.query(Equity)
            .order_by(desc(Equity.timestamp))
            .limit(limit)
            .all()[::-1]
        )
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "equity": e.equity
            } for e in rows
        ]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        db.close()


@app.get("/metrics")
def get_metrics(limit: int = Query(30, ge=1, le=500)):
    try:
        db = SessionLocal()
        decisions = (
            db.query(Decision)
            .order_by(desc(Decision.timestamp))
            .limit(limit)
            .all()
        )
        equity_map = {
            e.timestamp.replace(microsecond=0): e.equity
            for e in (
                db.query(Equity)
                .order_by(desc(Equity.timestamp))
                .limit(limit)
                .all()
            )
        }
        result = []
        for d in decisions:
            trend = volatility = tick = None
            try:
                parsed = json.loads(d.details)
                trend = parsed.get("trend")
                volatility = parsed.get("volatility")
                tick = parsed.get("tick")
            except Exception:
                trend_match = re.search(r"trend=([A-Z_]+)", d.details)
                vol_match = re.search(r"volatility=([\d\.]+)", d.details)
                tick_match = re.search(r"tick=([\d]+)", d.details)
                if trend_match:
                    trend = trend_match.group(1)
                if vol_match:
                    volatility = float(vol_match.group(1))
                if tick_match:
                    tick = int(tick_match.group(1))
            equity_val = equity_map.get(
                d.timestamp.replace(microsecond=0)
            )
            result.append({
                "timestamp": d.timestamp.isoformat(),
                "trend": trend,
                "volatility": volatility,
                "tick": tick,
                "equity": equity_val
            })
        return result[::-1]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        db.close()


@app.get("/logs")
@app.get("/logs/ai")
def get_logs(limit: int = Query(30, ge=1, le=500)):
    try:
        db = SessionLocal()
        logs = (
            db.query(LogEntry)
            .order_by(desc(LogEntry.timestamp))
            .limit(limit)
            .all()
        )
        return [
            {
                "timestamp": log.timestamp.isoformat(),
                "event": log.event,
                "details": log.details
            } for log in logs
        ]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        db.close()


@app.get("/status")
def get_status():
    try:
        stats = compute_stats()
        return {
            "api": check_api(),
            "ticks": check_ticks(),
            "bot": check_bot_status(),
            "last_decision": get_last_decision(),
            **stats
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/performance")
def get_performance():
    try:
        stats = compute_stats()
        final_balance = stats.get("final_balance", 0)
        pnl = final_balance - 10000
        return {
            "pnl": round(pnl, 2),
            "winrate": stats.get("winrate"),
            "drawdown": stats.get("drawdown"),
            "trades": stats.get("trades"),
            "sharpe": stats.get("sharpe"),
            "sortino": stats.get("sortino")
        }
    except Exception as e:
        return JSONResponse(
            content={"error": f"Błąd /performance: {str(e)}"},
            status_code=500
        )


@app.get("/metrics/live")
def metrics_live():
    return JSONResponse(
        content={"error": "Metrics not connected yet"},
        status_code=501
    )


def compute_stats():
    db = SessionLocal()
    try:
        equity_rows = (
            db.query(Equity)
            .order_by(desc(Equity.timestamp))
            .limit(200)
            .all()[::-1]
        )
        equity = [e.equity for e in equity_rows]
        drawdown = 0.0
        final_balance = equity[-1] if equity else 0.0
        peak = equity[0] if equity else 0.0
        for val in equity:
            if val > peak:
                peak = val
            dd = (peak - val) / peak if peak else 0.0
            drawdown = max(drawdown, dd)
        total = db.query(Decision).count()
        wins = db.query(Decision).filter(
            Decision.decision.in_(["win", "tp", "take_profit"])
        ).count()
        winrate = wins / total if total > 0 else 0.0
        returns = (
            [equity[i + 1] - equity[i] for i in range(len(equity) - 1)]
            if len(equity) > 1 else []
        )
        sharpe = sortino = None
        if returns:
            mean_ret = sum(returns) / len(returns)
            std_ret = (
                (
                    sum((r - mean_ret) ** 2 for r in returns) / len(returns)
                ) ** 0.5
                if len(returns) > 1 else 0
            )
            downside = [r for r in returns if r < 0]
            std_down = (
                (
                    sum((r - mean_ret) ** 2 for r in downside) / len(downside)
                ) ** 0.5
                if downside else 0
            )
            sharpe = round(mean_ret / std_ret, 2) if std_ret else None
            sortino = round(mean_ret / std_down, 2) if std_down else None
        return {
            "final_balance": final_balance,
            "drawdown": round(drawdown * 100, 2),
            "winrate": round(winrate * 100, 2),
            "open_trades": 0,
            "trades": total,
            "sharpe": sharpe,
            "sortino": sortino
        }
    finally:
        db.close()


def get_last_decision():
    try:
        db = SessionLocal()
        last = (
            db.query(Decision)
            .order_by(desc(Decision.timestamp))
            .first()
        )
        if last:
            return {
                "timestamp": last.timestamp.isoformat(),
                "decision": last.decision,
                "details": last.details
            }
        return None
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def parse_details(details: str):
    regexes = {
        "trend": r"trend=([A-Z_]+)",
        "volatility": r"volatility=([\d\.]+)",
        "symbol": r"symbol=([A-Z0-9]+)",
        "strategy": r"strategy=([a-zA-Z0-9_]+)",
        "status": r"status=([a-zA-Z0-9_]+)",
        "source": r"source=(LLM|metrics|manual)"
    }
    return {
        k: (re.search(rx, details).group(1)
            if re.search(rx, details) else None)
        for k, rx in regexes.items()
    }


def parse_decision_row(row):
    try:
        if not isinstance(row, list) or len(row) < 2:
            return {"error": "Invalid row format"}
        timestamp, decision = row[0], row[1]
        details = row[2] if len(row) > 2 else ""
        parsed = parse_details(details)
        return {
            "timestamp": timestamp,
            "decision": decision,
            **parsed,
            "details": details
        }
    except Exception as e:
        return {"error": f"Error parsing row: {str(e)}"}


import datetime
from core.db_models import SessionLocal, Decision, Equity, LogEntry
from sqlalchemy.orm import Session


def ms_to_datetime(ts):
    if ts is None:
        return None
    if isinstance(ts, datetime.datetime):
        return ts
    try:
        # If ts is in ms (int/float, > 1e10), convert to seconds
        if isinstance(ts, (int, float)) and ts > 1e10:
            return datetime.datetime.fromtimestamp(ts / 1000.0)
        # If ts is in seconds (int/float), convert directly
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(ts)
        # If ts is a string, try parsing
        if isinstance(ts, str):
            # Try ISO format first
            try:
                return datetime.datetime.fromisoformat(ts)
            except Exception:
                pass
            # Try as float (ms or s)
            try:
                tsf = float(ts)
                if tsf > 1e10:
                    return datetime.datetime.fromtimestamp(tsf / 1000.0)
                return datetime.datetime.fromtimestamp(tsf)
            except Exception:
                pass
    except Exception:
        pass

    return None


def save_decision_to_db(timestamp, decision, details=None):
    db: Session = SessionLocal()
    dec = Decision(
        timestamp=ms_to_datetime(timestamp),
        decision=decision,
        details=details
    )
    db.add(dec)
    db.commit()
    db.close()


def save_equity_to_db(timestamp, equity, pnl):
    db: Session = SessionLocal()
    eq = Equity(
        timestamp=ms_to_datetime(timestamp),
        equity=equity,
        pnl=pnl
    )
    db.add(eq)
    db.commit()
    db.close()


def save_log_to_db(event, details=None):
    db: Session = SessionLocal()
    log = LogEntry(
        timestamp=ms_to_datetime(datetime.datetime.now()),
        event=event,
        details=details
    )
    db.add(log)
    db.commit()
    db.close()

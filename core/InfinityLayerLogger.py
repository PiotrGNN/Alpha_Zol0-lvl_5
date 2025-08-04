# InfinityLayerLogger.py – logowanie zdarzeń, decyzji, statusów dla warstwy ∞

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class InfinityLayerLogger:

    def log(self, event: str, details: Dict = None):
        # Zapisz log do bazy danych przez save_log_to_db
        from core.db_utils import save_log_to_db
        import json
        save_log_to_db(event=event, details=json.dumps(details or {}))
        logging.info(
            (
                f"InfinityLayerLogger: logged to DB: event={event}, "
                f"details={details}"
            )
        )

    def get_logs(self, event: str = None):
        if event:
            return [log for log in self.logs if log["event"] == event]
        return self.logs

    def summary(self):
        return {
            "total": len(self.logs),
            "events": list(set(log["event"] for log in self.logs)),
        }

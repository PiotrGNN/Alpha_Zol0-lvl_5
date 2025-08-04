"""
# ✅ Audited by Copilot AI — 2025-07-29
# Changes: PEP8 line length fixes, audit header added, ensured logger and
# imports are correct.
"""

# main.py – Entry point for ZoL0 Bot with CLI, restart and simulation mode
import argparse
import logging
import sys
import threading
import time

import uvicorn
from core.BotCore import run_bot

logger = logging.getLogger("zol0-main")
logging.basicConfig(level=logging.INFO)


def start_api():
    """Start FastAPI dashboard backend."""
    try:
        uvicorn.run(
            "api_status:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False,
        )
    except Exception as e:
        logger.error(f"[API] Failed to start FastAPI server: {e}")


def main():
    parser = argparse.ArgumentParser(description="ZoL0 Bot entrypoint")
    parser.add_argument(
        "--mode",
        choices=["simulate", "live"],
        default="live",
        help="Run mode (simulate/live)",
    )
    parser.add_argument(
        "--no-api", action="store_true", help="Disable FastAPI dashboard"
    )
    parser.add_argument(
        "--autorestart",
        type=int,
        default=5,
        help="Restart delay (in seconds) on crash",
    )
    args = parser.parse_args()

    logger.info(
        f"ZoL0 Starting in {args.mode.upper()} mode. "
        f"API enabled: {not args.no_api}"
    )

    # Start API in background
    if not args.no_api:
        api_thread = threading.Thread(target=start_api, daemon=True)

        # [TASK-ID: system_monitoring_init]
        # Monitoring zasobów – uruchamiany pasywnie, nie wpływa na pętlę handlu
        # (Podpięcie tylko tutaj, nie w pętli decyzyjnej)
        api_thread.start()
        logger.info("[API] FastAPI server thread started")

    # Main bot loop with autorestart
    while True:
        try:
            run_bot(simulate=(args.mode == "simulate"))
        except KeyboardInterrupt:
            logger.info("[MAIN] ZoL0 shutdown requested by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"[MAIN] Bot crashed: {e}", exc_info=True)
            logger.info(f"[MAIN] Restarting in {args.autorestart} seconds...")
            time.sleep(args.autorestart)


if __name__ == "__main__":
    main()

# Export FastAPI app for uvicorn/Dockerfile

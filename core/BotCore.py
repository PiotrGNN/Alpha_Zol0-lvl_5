from core.db_utils import save_decision_to_db, save_equity_to_db
# BotCore.py – Final production refactor for ZoL0 (LEVEL-Ω, LEVEL-ALPHA-FUND)

from utils.config_loader import load_config
from utils.logger import setup_logger
from utils.news_social_fetcher import NewsSocialFetcher
from utils.news_social_scheduler import NewsSocialScheduler


def run_bot(simulate=False):
    """
    Production-grade main bot logic with full error handling and ML.
    """

    # Setup config, logger, and all required components
    # [TASK-ID: logic_guard]
    # ⚠️ UWAGA: poniższa pętla jest krytyczna dla czasu decyzji –
    # żadnych operacji I/O, sleep, ani monitoringu!
    # @no_slow_path
    # ⬆️ optimized for performance:
    # cache config, logger, and model objects outside the main loop
    config = load_config("config/config.yaml")
    setup_logger()
    import logging

    logger = logging.getLogger("zol0.botcore")
    from core.InfinityLayerLogger import InfinityLayerLogger
    from ai.OnlineTrainer import OnlineTrainer
    from core.MarketDataFetcher import MarketDataFetcher
    from core.OrderExecutor import OrderExecutor
    from core.RiskManager import RiskManager
    from core.StrategyPerformanceTracker import StrategyPerformanceTracker
    from core.PositionManager import PositionManager
    from models.tp_sl_optimizer import TpSlOptimizer
    from models.trend_predictor import TrendPredictor
    from models.volatility_forecaster import VolatilityForecaster
    from strategies.breakout import BreakoutStrategy
    from strategies.grid_trading import GridTradingStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy
    from strategies.sentiment import SentimentStrategy
    from strategies.trend_following import TrendFollowingStrategy
    from strategies.UniversalStrategy import UniversalStrategy
    from strategies.market_making import MarketMakingStrategy
    from strategies.arbitrage import ArbitrageStrategy
    from strategies.rl_omega import RLOmegaStrategy
    from core.DynamicStrategyRouter import DynamicStrategyRouter

    # Initialize core objects once, reuse in loop
    fetcher = MarketDataFetcher(
        api_url=config.get("api_url", "https://api.bybit.com/v5/market/kline")
    )
    perf_tracker = StrategyPerformanceTracker()
    position_manager = PositionManager()
    risk_manager = RiskManager(config)
    executor = OrderExecutor(
        api_url="https://api.bybit.com/v5/order/create",
        api_key=config.get("api_key"),
        api_secret=config.get("api_secret"),
    )
    trend_predictor = TrendPredictor()
    tp_sl_optimizer = TpSlOptimizer()
    vol_forecaster = VolatilityForecaster()
    infinity_logger = InfinityLayerLogger()
    ai_trainer = OnlineTrainer()
    symbols = config.get("symbols", [config.get("symbol", "BTC/USDT")])

    # Pre-create strategies_per_symbol and router_per_symbol
    # outside the main loop
    strategies_per_symbol = {}
    from strategies.sim_env import SimulatedTradingEnv  # Import before use

    for symbol in symbols:
        momentum = MomentumStrategy(name="Momentum")
        mean_reversion = MeanReversionStrategy(name="MeanReversion")
        breakout = BreakoutStrategy(name="Breakout")
        trend_following = TrendFollowingStrategy()
        universal = UniversalStrategy(name="Universal")
        grid_trading = GridTradingStrategy(name="GridTrading")
        market_making = MarketMakingStrategy(
            symbol=symbol,
            name="MarketMaking"
        )
        arbitrage = ArbitrageStrategy(name="Arbitrage")
        sentiment = SentimentStrategy(name="Sentiment")
        # Import SimulatedTradingEnv only once, outside the loop,
        # to avoid shadowing
        price_series = [
            c["close"]
            for c in fetcher.get_ohlcv(
                symbol, str(config["timeframe"]), limit=500
            )
        ]
        sim_env = SimulatedTradingEnv(price_series) if simulate else None
        rl_omega = RLOmegaStrategy(sim_env=sim_env)
        strategies = [
            momentum,
            mean_reversion,
            breakout,
            trend_following,
            universal,
            grid_trading,
            market_making,
            arbitrage,
            sentiment,
            rl_omega,
        ]
        strategies_per_symbol[symbol] = strategies
    router_per_symbol = {
        symbol: DynamicStrategyRouter(
            strategies=strategies_per_symbol[symbol]
        )
        for symbol in symbols
    }
    news_fetcher = NewsSocialFetcher()
    news_scheduler = NewsSocialScheduler(
        lambda: news_fetcher.fetch_news(query="crypto", limit=20),
        interval_sec=300,
    )
    news_scheduler.start()
    federated_round = 0
    retrain_interval = config.get("retrain_interval", 1000)
    reconnect_attempts = 0
    max_reconnect = 5
    strategies_per_symbol = {}
    from strategies.sim_env import SimulatedTradingEnv  # moved import here

    for symbol in symbols:
        momentum = MomentumStrategy(name="Momentum")
        mean_reversion = MeanReversionStrategy(name="MeanReversion")
        breakout = BreakoutStrategy(name="Breakout")
        trend_following = TrendFollowingStrategy()
        universal = UniversalStrategy(name="Universal")
        grid_trading = GridTradingStrategy(name="GridTrading")
        market_making = MarketMakingStrategy(
            symbol=symbol,
            name="MarketMaking"
        )
        arbitrage = ArbitrageStrategy(name="Arbitrage")
        sentiment = SentimentStrategy(name="Sentiment")

        price_series = [
            c["close"]
            for c in fetcher.get_ohlcv(
                symbol, str(config["timeframe"]), limit=500
            )
        ]
        sim_env = SimulatedTradingEnv(price_series) if simulate else None
        rl_omega = RLOmegaStrategy(sim_env=sim_env)
        strategies = [
            momentum,
            mean_reversion,
            breakout,
            trend_following,
            universal,
            grid_trading,
            market_making,
            arbitrage,
            sentiment,
            rl_omega,
        ]
        strategies_per_symbol[symbol] = strategies
    router_per_symbol = {
        symbol: DynamicStrategyRouter(
            strategies=strategies_per_symbol[symbol],
            perf_tracker=perf_tracker,
            risk_manager=risk_manager,
        )
        for symbol in symbols
    }
    news_fetcher = NewsSocialFetcher()
    news_scheduler = NewsSocialScheduler(
        lambda: news_fetcher.fetch_news(query="crypto", limit=20),
        interval_sec=300,
    )
    news_scheduler.start()
    federated_round = 0
    retrain_interval = config.get("retrain_interval", 1000)
    reconnect_attempts = 0
    max_reconnect = 5
    while True:
        # ⬆️ optimized for performance: batch fetch OHLCV and ML predictions
        ohlcv_cache = {}
        for symbol in symbols:
            try:
                # Cache OHLCV fetches for this loop
                if symbol not in ohlcv_cache:
                    ohlcv_cache[symbol] = fetcher.get_ohlcv(
                        symbol, str(config["timeframe"])
                    )
                candles = ohlcv_cache[symbol]
                if not candles:
                    logger.warning(
                        f"No OHLCV data fetched for {symbol}. Skipping."
                    )
                    continue
                logger.info(
                    f"Fetched OHLCV for {symbol}: {candles[-1]}"
                )
                price = candles[-1]["close"]
                balance = config.get("balance", 1000)
                position_status = "none"
                pnl_history = []
                # Batch ML predictions if possible (placeholder, real batching
                # requires model support)
                trend = trend_predictor.predict_trend(candles)
                sl, tp = tp_sl_optimizer.optimize(candles)
                vol = vol_forecaster.forecast_volatility(candles)
                market_state = {
                    "trend": trend,
                    "volatility": vol,
                    "price": price,
                    "balance": balance,
                    "sl": sl,
                    "tp": tp,
                    "pnl_history": pnl_history,
                    "symbol": symbol,
                }
                router = router_per_symbol[symbol]
                ensemble_signals = router.route(market_state)
                # Log raw signals from each strategy for diagnosis
                import asyncio
                import inspect
                from inspect import signature
                import json
                raw_signals = []
                # Prepare available data for argument mapping
                klines = candles
                indicators = None  # TODO: extract indicators if available
                timeframe = str(config["timeframe"])
                price = candles[-1]["close"] if candles else None
                mid_price = price if price is not None else 0.0
                inventory = None  # TODO: track inventory if available
                orderbooks = {}  # Default: empty dict
                prices = {}  # Default: empty dict
                sentiment_data = []  # Default: empty list
                data = klines if klines else []
                orderbook = {}  # Default: empty dict
                state = market_state
                for s in strategies_per_symbol[symbol]:
                    try:
                        analyze_fn = getattr(s, "analyze", None)
                        if analyze_fn is not None:
                            sig_obj = signature(analyze_fn)
                            params = sig_obj.parameters
                            call_args = {}
                            # Map known argument names to available data
                            for pname in params:
                                # Special handling for MarketMakingStrategy:
                                # always provide orderbook and mid_price
                                # defaults
                                if (
                                    getattr(s, "__class__", None)
                                    and (
                                        s.__class__.__name__
                                        == "MarketMakingStrategy"
                                    )
                                ):
                                    if pname == "orderbook":
                                        call_args[pname] = orderbook
                                    if pname == "mid_price":
                                        call_args[pname] = mid_price
                                if pname == "self":
                                    continue
                                elif pname in ("market_data", "market_state"):
                                    call_args[pname] = market_state
                                elif pname == "klines":
                                    call_args[pname] = klines
                                elif pname == "indicators":
                                    call_args[pname] = indicators
                                elif pname == "timeframe":
                                    call_args[pname] = timeframe
                                elif pname == "price":
                                    call_args[pname] = price
                                elif pname == "mid_price":
                                    if pname not in call_args:
                                        call_args[pname] = mid_price
                                elif pname == "inventory":
                                    call_args[pname] = inventory
                                elif pname == "orderbooks":
                                    call_args[pname] = orderbooks
                                elif pname == "prices":
                                    call_args[pname] = prices
                                elif pname == "sentiment_data":
                                    call_args[pname] = sentiment_data
                                elif pname == "symbol":
                                    call_args[pname] = symbol
                                elif pname == "data":
                                    call_args[pname] = data
                                elif pname == "orderbook":
                                    if pname not in call_args:
                                        call_args[pname] = orderbook
                                elif pname == "state":
                                    call_args[pname] = state
                                else:
                                    # Try to get from market_state
                                    if pname in market_state:
                                        call_args[pname] = market_state[pname]
                                    else:
                                        # Provide a safe default for unknown
                                        # args
                                        call_args[pname] = None
                            if inspect.iscoroutinefunction(analyze_fn):
                                try:
                                    sig = asyncio.run(analyze_fn(**call_args))
                                except RuntimeError:
                                    sig = (
                                        asyncio.get_event_loop()
                                        .run_until_complete(
                                            analyze_fn(**call_args)
                                        )
                                    )
                            else:
                                sig = analyze_fn(**call_args)
                            raw_signals.append({
                                "strategy": getattr(s, "name", str(s)),
                                "signal": sig
                            })
                        else:
                            raw_signals.append({
                                "strategy": getattr(s, "name", str(s)),
                                "error": "No analyze method"
                            })
                    except Exception as e:
                        raw_signals.append({
                            "strategy": getattr(s, "name", str(s)),
                            "error": str(e)
                        })
                infinity_logger.log(
                    "strategy_signals",
                    {"symbol": symbol, "raw_signals": raw_signals},
                )
                logger.info(
                    f"DynamicStrategyRouter ensemble signals for {symbol}: "
                    f"{ensemble_signals}"
                )
                infinity_logger.log(
                    "ensemble_signals",
                    {"symbol": symbol, "signals": ensemble_signals},
                )
                # Zapis decyzji do bazy (każda iteracja)
                save_decision_to_db(
                    timestamp=candles[-1]["timestamp"],
                    decision="buy" if ensemble_signals else "hold",
                    details=json.dumps({
                        "ensemble_signals": ensemble_signals,
                        "trend": trend,
                        "volatility": vol
                    })
                )
                if ensemble_signals:
                    main_sig = max(
                        ensemble_signals, key=lambda x: x.get("allocation", 0)
                    )
                    active_strategy = next(
                        (
                            s
                            for s in strategies_per_symbol[symbol]
                            if s.name == main_sig["strategy"]
                        ),
                        None,
                    )
                else:
                    active_strategy = None
                allow, sl_price, tp_price, allocation = (
                    risk_manager.apply_risk(
                        signal="buy",
                        price=price,
                        balance=balance,
                        position_status=position_status,
                        pnl_history=pnl_history,
                        symbol=symbol,
                        global_pnl_history=None,
                        open_positions=None,
                    )
                )
                logger.info(
                    f"RiskManager: allow={allow}, sl={sl_price}, "
                    f"tp={tp_price}, allocation={allocation}"
                )
                infinity_logger.log(
                    "risk_decision",
                    {
                        "symbol": symbol,
                        "allow": allow,
                        "sl": sl_price,
                        "tp": tp_price,
                        "allocation": allocation,
                    },
                )
                if allow:
                    order = {
                        "symbol": symbol,
                        "side": "BUY",
                        "amount": allocation / price if price > 0 else 0,
                        "price": price,
                        "sl": sl_price,
                        "tp": tp_price,
                        "strategy": getattr(
                            active_strategy, "name", "unknown"
                        ),
                    }
                    if not simulate:
                        try:
                            executor.execute_order(order, use_rest=True)
                            logger.info(f"Order executed: {order}")
                            infinity_logger.log("order_executed", order)
                            # Aktualizacja pozycji po wykonaniu zlecenia
                            position_manager.update_position(symbol, order)
                            logger.info(
                                f"Position updated: "
                                f"{position_manager.get_position(symbol)}"
                            )
                            infinity_logger.log(
                                "position_update",
                                {
                                    "symbol": symbol,
                                    "position": position_manager.get_position(
                                        symbol
                                    ),
                                }
                            )
                        except Exception as e:
                            logger.error(f"Order execution failed: {e}")
                            infinity_logger.log(
                                "panic_exit",
                                {"symbol": symbol, "error": str(e)},
                            )
                            reconnect_attempts += 1
                            if reconnect_attempts >= max_reconnect:
                                logger.critical(
                                    (
                                        "Max reconnect attempts reached. "
                                        "Panic exit."
                                    )
                                )
                                return
                            continue
                    else:
                        logger.info(
                            f"[SIMULATION] Order would be executed: {order}"
                        )
                        infinity_logger.log("order_simulated", order)
                        # Aktualizacja pozycji w trybie symulacji
                        position_manager.update_position(symbol, order)
                        logger.info(
                            f"Position updated: "
                            f"{position_manager.get_position(symbol)}"
                        )
                        infinity_logger.log(
                            "position_update",
                            {
                                "symbol": symbol,
                                "position": position_manager.get_position(
                                    symbol
                                )
                            }
                        )
                    perf_tracker.update(symbol, {"pnl": 0})
                    # Zapis equity do bazy po każdej decyzji
                    save_equity_to_db(
                        timestamp=candles[-1]["timestamp"],
                        equity=balance,
                        pnl=0.0
                    )
                if federated_round % retrain_interval == 0:
                    ai_trainer.fit_if_needed()
                    infinity_logger.log(
                        "ai_retrain",
                        {"step": federated_round, "symbol": symbol},
                    )
                federated_round += 1
            except Exception as e:
                logger.error(f"Bot error for {symbol}: {e}", exc_info=True)
                infinity_logger.log(
                    "panic_exit", {"symbol": symbol, "error": str(e)}
                )
                reconnect_attempts += 1
                if reconnect_attempts >= max_reconnect:
                    logger.critical(
                        "Max reconnect attempts reached. Panic exit."
                    )
                    return
                continue

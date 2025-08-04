# ZoL0-Level-0-5.md – Pełna Checklista Budowy AI Trading Bota od Zera

**Uwaga: Od LEVEL-Ω cała logika decyzji, equity i logów została przeniesiona do bazy danych Postgres. API oraz worker komunikują się wyłącznie przez bazę – nie są już używane pliki CSV ani logi lokalne. Szczegóły: core/db_models.py, core/db_utils.py, api_status.py, core/BotCore.py.**

🔰 **LEVEL 0 – Fundamenty i struktura projektu**  
Cel: uruchomić najprostszy działający bot z modularną strukturą, lokalnym main.py, loggingiem i configiem.

**Postęp: 9/9**
- [x] 0.1 – Utwórz strukturę katalogów: `core/`, `models/`, `strategies/`, `utils/`, `config/`, `logs/`, `tests/`
- [x] 0.2 – `start.sh` i `main.py` – punkt wejścia bota
- [x] 0.3 – `config/config.yaml` – parametry (symbol, interwał, SL/TP, API keys)
- [x] 0.4 – `core/MarketDataFetcher.py` – pobieranie danych OHLCV z Bybit (REST i WebSocket)
- [x] 0.5 – `core/OrderExecutor.py` – mockowa egzekucja zleceń (na początek tylko log)
- [x] 0.6 – `utils/logger.py` – system logowania akcji bota
- [x] 0.7 – `utils/config_loader.py` – ładowanie plików YAML/ENV
- [x] 0.8 – `tests/test_marketdata_fetcher.py` – testy pobierania danych
- [x] 0.9 – **Commit**: `LEVEL 0 – Bot skeleton ready`

🧠 **LEVEL 1 – Prosta strategia i egzekucja**  
Cel: stworzyć podstawowy silnik decyzyjny i strategię (SMA/EMA).

**Postęp: 6/6**
- [x] 1.1 – `strategies/SmaCrossStrategy.py` – klasyczna strategia przecięcia średnich
- [x] 1.2 – `core/AIStrategyEngine.py` – integracja danych i decyzji
- [x] 1.3 – `core/PositionManager.py` – śledzenie pozycji otwartych i zamkniętych
- [x] 1.4 – `core/OrderExecutor.py` – wysyłanie zleceń na Bybit (BUY/SELL/TP/SL)
- [x] 1.5 – `tests/test_strategy_engine.py` – test decyzji BUY/SELL
- [x] 1.6 – **Commit**: `LEVEL 1 – Live strategy execution works`

🧠 **LEVEL 2 – Risk i backtesting**  
Cel: kontrola ryzyka, testy na danych historycznych

**Postęp: 5/5**
- [x] 2.1 – `core/RiskManager.py` – alokacja, SL/TP, drawdown limits
- [x] 2.2 – `utils/backtesting.py` – silnik symulacyjny do testów offline
- [x] 2.3 – `utils/health_check.py` – walidacja API, ticków, statusu bota
- [x] 2.4 – `tests/test_risk_manager.py`, `test_backtester.py`
- [x] 2.5 – **Commit**: `LEVEL 2 – Risk management + backtest`

🧠 **LEVEL 3 – AI: klasyfikacja i ML**  
Cel: wprowadzenie predykcji trendu, wolumenu, zmienności

**Postęp: 6/6**
- [x] 3.1 – `models/trend_predictor.py` – klasyfikacja (↑/↓/→)
- [x] 3.2 – `models/volatility_forecaster.py` – regresja zmienności
- [x] 3.3 – `models/ai_utils.py` – pipeline danych OHLCV → wektory
- [x] 3.4 – Integracja z `AIStrategyEngine.py`: predykcja jako sygnał
- [x] 3.5 – `tests/test_ai_model_logic.py`
- [x] 3.6 – **Commit**: `LEVEL 3 – AI-based prediction integrated`

🧠 **LEVEL 4 – Meta-strategie i optymalizacja**  
Cel: inteligentne zarządzanie strategiami i adaptacja parametrów

**Postęp: 7/7**
- [x] 4.1 – `strategies/DynamicStrategyRouter.py` – dynamiczne przełączanie strategii
- [x] 4.2 – `models/tp_sl_optimizer.py` – optymalizacja TP/SL
- [x] 4.3 – `models/time_advantage.py` – wykrywanie przewagi czasowej
- [x] 4.4 – `models/anti_pattern_guard.py` – wykrywanie fałszywych sygnałów
- [x] 4.5 – `models/portfolio_optimizer.py` – RL lub scoring do rotacji strategii
- [x] 4.6 – `core/StrategyPerformanceTracker.py` – ocena każdej strategii
- [x] 4.7 – **Commit**: `LEVEL 4 – Meta-layer + strategy optimization`

🔐 **LEVEL 5 – ZTA, FL i system zysków**  
Cel: wprowadzenie warstw bezpieczeństwa i uczenia rozproszonego

**Postęp: 10/10**
**5A – Zero-Trust Architecture**
- [x] `security/zero_trust.py`: `validate_input`, `authorize`, `log_event`
- [x] Role i tokeny z ENV
- [x] Logika ochrony krytycznych modułów (np. AI decision → OrderExecutor)

**5B – Federated Learning**
- [x] `fl/training.py`: `train_local_model`, `aggregate_models`
- [x] `fl/runner.py`: symulacja klientów, aktualizacja modelu globalnego
- [x] `config/level5.py`: ścieżki, parametry, `fl_round_limit`

**5C – Profit Layer Optimization**
- [x] `models/trend_predictor.py`: uaktualnienie pod FL
- [x] `tp_sl_optimizer.py`, `time_advantage.py`, `anti_pattern_guard.py` – tuning z danych
- [x] `zero_drawdown_guard.py`: wykrycie/stop drawdownu
- [x] `tests/test_profit_layers.py`: testy predykcji, SL/TP, guardów

**Finał:**
- [x] Spięcie FL + ZTA + wszystkie strategie
- [x] **Commit**: `LEVEL 5 – Full AI Profit System + Security Ready`


📦 **Deployment & DevOps** *(równolegle do poziomów)*
**Postęp: 6/6**
- [x] `Dockerfile`, `secrets.env`, `render.yaml`
- [x] GitHub Actions (test + build)
- [x] `README.md`, `DEVELOPMENT.md`, `TODO.md`, `copilot_taskplan.yaml`
- [x] **Migracja: decyzje, equity i logi zapisywane wyłącznie do bazy Postgres (brak plików CSV/logów lokalnych)**

✅ **FINAŁ:**  
Bot gotowy do produkcji z pełnym AI stackiem, federacyjnym uczeniem, zabezpieczeniami i systemem optymalizacji zysków.

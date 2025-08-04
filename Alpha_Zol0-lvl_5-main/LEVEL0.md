# ZoL0 – LEVEL 0 TASKLIST
## Zadania
1. Utwórz szkielet projektu, pliki bazowe, config, logger, mock MarketDataFetcher/OrderExecutor
2. main.py uruchamia skeleton
3. Testy: pytest, logi
4. Commit: "LEVEL 0 – Bot skeleton ready"

Status: ✅ Zrealizowano
# ZoL0 – LEVEL 0 TASKLIST
# Cel: uruchomić najprostszy działający szkielet AI trading bota z modularną strukturą, plikiem main.py, loggingiem i configiem.
# Zrób dokładnie to:
# 0.1 – Stwórz strukturę katalogów: core/, models/, strategies/, utils/, config/, logs/, tests/
# 0.2 – Utwórz start.sh i main.py jako punkt wejścia
#       → main.py ma ładować config, inicjalizować logger i symulacyjnie odpalać core/MarketDataFetcher + OrderExecutor
# 0.3 – Stwórz config/config.yaml z przykładowymi parametrami (symbol, interwał, SL/TP, klucze API)
# 0.4 – core/MarketDataFetcher.py – funkcja get_ohlcv(symbol, interval), mock pobierający dane OHLCV
# 0.5 – core/OrderExecutor.py – funkcja execute_order(order), która tylko loguje co by zrobiła (mock trading)
# 0.6 – utils/logger.py – zdefiniuj logger, zapisuj do logs/bot.log
# 0.7 – utils/config_loader.py – funkcja load_config(path), zwracająca dict z YAML
# 0.8 – tests/test_marketdata_fetcher.py – napisz pytest do get_ohlcv
# 0.9 – Zakończ commitem: "LEVEL 0 – Bot skeleton ready"
# Używaj komentarzy z "# ZoL0 LEVEL 0" do oznaczania kodu. Każda funkcja ma mieć dok. string i być gotowa do testowania.
# Gotowe do rozszerzenia w kolejnych LEVELach. Kod nie może być placeholderem – ma działać od razu po `python main.py`.
# Podstawowe zasady:
# - Używaj pathlib, yaml, logging, pytest
# - Przechowuj logi w logs/
# - config.yaml ma zawierać symbol, timeframe, sl_pct, tp_pct, api_key, api_secret
# - Nie używaj zewnętrznych bibliotek poza standardowymi i PyYAML
# Wszystkie pliki mają działać lokalnie. Nie łącz się z prawdziwym API – mockuj dane.
# Startuj.
# 🧠 Po zakończeniu:
# ✔ Uruchom python main.py
# ✔ Sprawdź logs/bot.log
# ✔ Odpal pytest tests/test_marketdata_fetcher.py
# ✔ Zrób commit:
# git add .
# git commit -m "LEVEL 0 – Bot skeleton ready"
# Skopiuj powyższy komentarz do pliku LEVEL0.md lub użyj jako prompt dla Copilota w VS Code.
# LEVEL0.md – Checklist LEVEL 0

## Zadania
- [ ] Utwórz strukturę katalogów: core/, models/, strategies/, utils/, config/, logs/, tests/
- [ ] Stwórz start.sh i main.py
- [ ] Skonfiguruj config/config.yaml
- [ ] Zaimplementuj core/MarketDataFetcher.py
- [ ] Zaimplementuj core/OrderExecutor.py (mock)
- [ ] Zaimplementuj utils/logger.py
- [ ] Zaimplementuj utils/config_loader.py
- [ ] Stwórz tests/test_marketdata_fetcher.py

## Testy
- [ ] tests/test_marketdata_fetcher.py

## Commit końcowy
- [ ] Commit: LEVEL 0 – Bot skeleton ready

## Zależności
- Brak (poziom startowy)

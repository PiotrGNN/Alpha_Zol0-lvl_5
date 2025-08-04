"""
Testy automatyczne i logi weryfikujące poprawność danych zwracanych
przez endpointy API ZoL0.
"""
import requests
import logging

API_URL = "http://localhost:8000"  # Zmień jeśli inny port/host

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


def test_performance():
    r = requests.get(f"{API_URL}/performance")
    assert r.status_code == 200, f"/performance status {r.status_code}"
    data = r.json()
    logging.info(f"/performance: {data}")
    assert isinstance(
        data.get("final_balance"), (int, float)
    ), "Brak lub niepoprawny final_balance"
    assert "winrate" in data, "Brak winrate"
    assert "drawdown" in data, "Brak drawdown"
    assert "trades" in data, "Brak trades"
    assert "sharpe" in data, "Brak sharpe"
    assert "sortino" in data, "Brak sortino"


def test_strategy():
    r = requests.get(f"{API_URL}/strategy")
    assert r.status_code == 200, f"/strategy status {r.status_code}"
    data = r.json()
    logging.info(f"/strategy: {data}")
    assert "strategies" in data, "Brak strategies"
    assert "modes" in data, "Brak modes"
    assert "params" in data, "Brak params"


def test_metrics():
    r = requests.get(f"{API_URL}/metrics")
    assert r.status_code == 200, f"/metrics status {r.status_code}"
    data = r.json()
    logging.info(f"/metrics: {data}")
    assert isinstance(data, list), "/metrics nie zwraca listy"
    if data:
        for m in data:
            assert "timestamp" in m, "Brak timestamp w metrics"
            assert "trend" in m, "Brak trend w metrics"
            assert "volatility" in m, "Brak volatility w metrics"
            assert "tick" in m, "Brak tick w metrics"
            assert "equity" in m, "Brak equity w metrics"


def test_equity():
    r = requests.get(f"{API_URL}/equity")
    assert r.status_code == 200, f"/equity status {r.status_code}"
    data = r.json()
    logging.info(f"/equity: {data}")
    assert isinstance(data, list), "/equity nie zwraca listy"
    if data:
        for e in data:
            assert "timestamp" in e, "Brak timestamp w equity"
            assert "equity" in e, "Brak equity w equity"


def run_all():
    logging.info("=== URUCHAMIANIE TESTÓW API ===")
    test_performance()
    test_strategy()
    test_metrics()
    test_equity()
    print("✅ Wszystkie testy przeszły pomyślnie!")


if __name__ == "__main__":
    run_all()

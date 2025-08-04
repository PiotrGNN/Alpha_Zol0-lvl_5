import requests

BASE_URL = (
    "https://zol0-backend.onrender.com"
)


def test_root():
    r = requests.get(f"{BASE_URL}/")
    print(f"/ status_code: {r.status_code}, response: {r.text}")
    assert r.status_code == 200, (
        f"Expected 200, got {r.status_code}: {r.text}"
    )


def test_strategy():
    r = requests.get(f"{BASE_URL}/strategy")
    print(f"/strategy status_code: {r.status_code}, response: {r.text}")
    assert r.status_code == 200, (
        f"Expected 200, got {r.status_code}: {r.text}"
    )


def test_status():
    r = requests.get(f"{BASE_URL}/status")
    print(f"/status status_code: {r.status_code}, response: {r.text}")
    assert r.status_code == 200, (
        f"Expected 200, got {r.status_code}: {r.text}"
    )


def test_decisions():
    r = requests.get(f"{BASE_URL}/decisions?limit=3")
    print(f"/decisions status_code: {r.status_code}, response: {r.text}")
    assert r.status_code == 200, (
        f"Expected 200, got {r.status_code}: {r.text}"
    )


def test_logs_ai():
    r = requests.get(f"{BASE_URL}/logs/ai?limit=3")
    print(f"/logs/ai status_code: {r.status_code}, response: {r.text}")
    assert r.status_code == 200, (
        f"Expected 200, got {r.status_code}: {r.text}"
    )


if __name__ == "__main__":
    test_root()
    test_strategy()
    test_status()
    test_decisions()
    test_logs_ai()

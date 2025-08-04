import requests


def test_api_status():
    # Upewnij się, że backend jest uruchomiony na localhost:8000
    try:
        response = requests.get("http://localhost:8000/status")
        assert response.status_code == 200
    except Exception:
        assert False, "API not reachable"

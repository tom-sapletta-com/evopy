import requests
import time

def wait_for_api_ready(url="http://127.0.0.1:5000/ping", timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                print("[PING] API gotowe!")
                return True
        except Exception:
            pass
        print("[PING] Oczekiwanie na API...")
        time.sleep(1)
    raise RuntimeError("API nie odpowiedziało w zadanym czasie!")

if __name__ == "__main__":
    wait_for_api_ready()

import time
from devopy.log_db import LogDB
from devopy.auto_heal import AutoHealer

def autoheal_loop(sleep_seconds=10):
    print("[AUTOHEAL] Start log auto-healing loop...")
    while True:
        rows = LogDB.fetch_recent(limit=50)
        for row in rows:
            if row[3] == "error" and row[7]:  # level == error and error message exists
                print(f"[AUTOHEAL] Detected error log id={row[0]}: {row[7][:80]}...")
                healed = AutoHealer.heal_from_log(row)
                if healed:
                    print(f"[AUTOHEAL] Healing attempt for log id={row[0]} succeeded.")
                else:
                    print(f"[AUTOHEAL] Healing attempt for log id={row[0]} failed or not applicable.")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    autoheal_loop()

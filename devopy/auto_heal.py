import importlib
import traceback
from log_db import LogDB
from auto_import import auto_import

class AutoHealer:
    """
    System LLM + heurystyki do wykrywania i naprawy błędów na podstawie logów.
    """
    def __init__(self, llm_analyze_error=None):
        # llm_analyze_error: funkcja LLM (np. z devopy.llm) do analizy błędów
        self.llm_analyze_error = llm_analyze_error

    def analyze_and_heal(self, log_row):
        """
        log_row: tuple z LogDB.fetch_recent(), zawiera m.in. error, request, response
        """
        error = log_row[7]  # error
        if not error:
            return False, "Brak błędu"

        # Heurystyka: brak modułu
        if "No module named" in error:
            import re
            match = re.search(r"No module named '([^']+)'", error)
            if match:
                pkg = match.group(1)
                auto_import([pkg])
                return True, f"Automatycznie zainstalowano brakujący pakiet: {pkg}"

        # LLM: analiza błędu (jeśli podpięta)
        if self.llm_analyze_error:
            suggestion = self.llm_analyze_error(error)
            if suggestion and suggestion.get("action") == "install":
                auto_import([suggestion["package"]])
                return True, f"LLM: zainstalowano {suggestion['package']} zgodnie z sugestią"
            # Możesz dodać inne typy napraw

        return False, "Brak automatycznej naprawy"

    def heal_recent_errors(self, limit=20):
        logs = LogDB.fetch_recent(limit)
        results = []
        for row in logs:
            ok, msg = self.analyze_and_heal(row)
            if ok:
                results.append((row[0], msg))
        return results

# Przykład użycia
if __name__ == "__main__":
    healer = AutoHealer()
    healed = healer.heal_recent_errors()
    for log_id, msg in healed:
        print(f"[AUTOHEAL] Log {log_id}: {msg}")

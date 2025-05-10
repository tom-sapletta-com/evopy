# Narzędzia monitorowania

Ten katalog zawiera skrypty i narzędzia do monitorowania zasobów i wydajności używane w projekcie Evopy.

## Dostępne narzędzia

- `monitor.py` - Główny moduł monitorowania
- `monitor_resources.py` - Monitorowanie zasobów systemowych (CPU, pamięć, dysk)
- `monitor_watchdog.sh` - Skrypt watchdog do monitorowania procesów
- `resource_monitor.sh` - Skrypt do uruchamiania monitora zasobów

## Przeznaczenie

Narzędzia w tym katalogu służą do:

1. Monitorowania zużycia zasobów (CPU, pamięć, dysk) podczas wykonywania kodu
2. Zbierania metryk wydajnościowych
3. Generowania raportów z monitoringu
4. Automatycznego wykrywania i reagowania na problemy z zasobami

## Użycie

```bash
# Uruchomienie monitora zasobów
./tools/monitoring/resource_monitor.sh

# Monitorowanie procesu z określonym PID
python tools/monitoring/monitor.py --pid 1234
```

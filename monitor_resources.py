#!/usr/bin/env python3
"""
Monitor zasobów systemowych dla projektu Evopy

Ten skrypt monitoruje zużycie zasobów systemowych (RAM, dysk) i podejmuje
działania naprawcze, gdy przekroczą określone progi.

Funkcje:
1. Monitorowanie zużycia RAM i podejmowanie działań gdy przekroczy 90%
2. Monitorowanie zużycia dysku i ograniczanie go do 100GB
3. Automatyczne czyszczenie plików logów i kontenerów Docker
4. Wykrywanie i usuwanie procesów zombie
"""

import os
import sys
import time
import psutil
import logging
import subprocess
import signal
from pathlib import Path
from datetime import datetime, timedelta

# Konfiguracja
MAX_RAM_PERCENT = 90  # Maksymalne zużycie RAM w procentach
MAX_DISK_USAGE = 100 * 1024 * 1024 * 1024  # 100GB w bajtach
LOG_ROTATION_SIZE = 100 * 1024 * 1024  # 100MB
LOG_ROTATION_COUNT = 5  # Liczba plików rotacji
CHECK_INTERVAL = 60  # Interwał sprawdzania w sekundach
EVOPY_DIR = Path(__file__).parent.absolute()
LOG_DIR = EVOPY_DIR / "logs"
LOG_FILE = LOG_DIR / "resource_monitor.log"

# Upewnij się, że katalog logów istnieje
os.makedirs(LOG_DIR, exist_ok=True)

# Konfiguracja logowania z rotacją
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_FILE, 
            maxBytes=LOG_ROTATION_SIZE, 
            backupCount=LOG_ROTATION_COUNT
        )
    ]
)

logger = logging.getLogger("evopy-resource-monitor")

class ResourceMonitor:
    """Klasa do monitorowania i zarządzania zasobami systemowymi"""
    
    def __init__(self):
        """Inicjalizacja monitora zasobów"""
        self.evopy_dir = EVOPY_DIR
        self.log_dir = LOG_DIR
        self.assistant_log = self.evopy_dir / "assistant.log"
        self.running = True
        
        # Rejestracja obsługi sygnałów
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
        
        logger.info(f"Monitor zasobów uruchomiony dla katalogu: {self.evopy_dir}")
    
    def _handle_interrupt(self, signum, frame):
        """Obsługa sygnału przerwania"""
        logger.info("Otrzymano sygnał przerwania. Kończenie pracy...")
        self.running = False
    
    def get_ram_usage(self):
        """Pobiera aktualne zużycie RAM w procentach"""
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self, path=None):
        """Pobiera aktualne zużycie dysku w bajtach"""
        if path is None:
            path = self.evopy_dir
        return psutil.disk_usage(path).used
    
    def get_evopy_disk_usage(self):
        """Pobiera rozmiar katalogu projektu Evopy"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.evopy_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    
    def rotate_log_file(self, log_file, max_size=LOG_ROTATION_SIZE, backup_count=LOG_ROTATION_COUNT):
        """Rotacja pliku logu, gdy przekroczy określony rozmiar"""
        if not os.path.exists(log_file):
            return
            
        file_size = os.path.getsize(log_file)
        if file_size < max_size:
            return
            
        logger.info(f"Rotacja pliku logu: {log_file} (rozmiar: {file_size / (1024*1024):.2f} MB)")
        
        # Usuń najstarszy plik rotacji, jeśli istnieje
        oldest_backup = f"{log_file}.{backup_count}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        
        # Przesuń istniejące pliki rotacji
        for i in range(backup_count - 1, 0, -1):
            src = f"{log_file}.{i}"
            dst = f"{log_file}.{i+1}"
            if os.path.exists(src):
                os.rename(src, dst)
        
        # Utwórz pierwszy plik rotacji
        if os.path.exists(log_file):
            os.rename(log_file, f"{log_file}.1")
        
        # Utwórz nowy, pusty plik logu
        open(log_file, 'w').close()
        logger.info(f"Utworzono nowy plik logu: {log_file}")
    
    def clean_docker_containers(self):
        """Czyści nieużywane kontenery Docker związane z Evopy"""
        try:
            # Znajdź wszystkie kontenery z prefiksem evopy
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=evopy", "--format", "{{.ID}}"],
                capture_output=True, text=True, check=True
            )
            
            container_ids = result.stdout.strip().split('\n')
            if container_ids and container_ids[0]:
                logger.info(f"Znaleziono {len(container_ids)} kontenerów Evopy do wyczyszczenia")
                
                # Usuń wszystkie znalezione kontenery
                for container_id in container_ids:
                    subprocess.run(
                        ["docker", "rm", "-f", container_id],
                        capture_output=True, text=True
                    )
                logger.info(f"Wyczyszczono {len(container_ids)} kontenerów Docker")
        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas czyszczenia kontenerów Docker: {e}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas czyszczenia kontenerów: {e}")
    
    def clean_zombie_processes(self):
        """Wykrywa i próbuje usunąć procesy zombie"""
        try:
            # Znajdź procesy zombie
            zombie_processes = []
            for proc in psutil.process_iter(['pid', 'status', 'name']):
                try:
                    if proc.info['status'] == 'zombie':
                        zombie_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if zombie_processes:
                logger.info(f"Znaleziono {len(zombie_processes)} procesów zombie")
                
                # Próba usunięcia procesów zombie
                for proc in zombie_processes:
                    try:
                        # Znajdź proces rodzica
                        parent = psutil.Process(proc.ppid())
                        logger.info(f"Proces zombie: {proc.pid} (rodzic: {parent.pid}, {parent.name()})")
                        
                        # Wyślij sygnał SIGCHLD do rodzica, aby odebrał status zakończenia
                        os.kill(parent.pid, signal.SIGCHLD)
                        logger.info(f"Wysłano SIGCHLD do procesu rodzica {parent.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        logger.error(f"Nie można obsłużyć procesu zombie {proc.pid}: {e}")
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia procesów zombie: {e}")
    
    def limit_log_file_size(self, log_file, max_size=100*1024*1024):
        """Ogranicza rozmiar pliku logu do określonego maksimum"""
        if not os.path.exists(log_file):
            return
            
        file_size = os.path.getsize(log_file)
        if file_size <= max_size:
            return
            
        logger.info(f"Ograniczanie rozmiaru pliku logu: {log_file} (obecny: {file_size / (1024*1024):.2f} MB, max: {max_size / (1024*1024):.2f} MB)")
        
        # Przytnij plik do określonego rozmiaru
        try:
            # Utwórz kopię zapasową
            backup_file = f"{log_file}.bak"
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
            # Kopiuj ostatnie N bajtów do pliku tymczasowego
            with open(log_file, 'rb') as src:
                src.seek(-max_size, 2)  # Przejdź do (rozmiar_pliku - max_size)
                data = src.read()
                
                with open(backup_file, 'wb') as dst:
                    dst.write(data)
            
            # Zastąp oryginalny plik
            os.remove(log_file)
            os.rename(backup_file, log_file)
            
            logger.info(f"Plik logu został ograniczony do {max_size / (1024*1024):.2f} MB")
        except Exception as e:
            logger.error(f"Błąd podczas ograniczania rozmiaru pliku logu: {e}")
    
    def clean_old_logs(self, max_age_days=30):
        """Usuwa stare pliki logów"""
        try:
            now = datetime.now()
            count = 0
            
            # Sprawdź pliki w katalogu logów
            for file in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, file)
                if os.path.isfile(file_path) and file.endswith('.log'):
                    # Sprawdź czas modyfikacji pliku
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    age = now - mtime
                    
                    if age.days > max_age_days:
                        os.remove(file_path)
                        count += 1
                        logger.info(f"Usunięto stary plik logu: {file_path} (wiek: {age.days} dni)")
            
            if count > 0:
                logger.info(f"Usunięto {count} starych plików logów")
        except Exception as e:
            logger.error(f"Błąd podczas usuwania starych logów: {e}")
    
    def check_and_manage_resources(self):
        """Sprawdza i zarządza zasobami systemowymi"""
        try:
            # Sprawdź zużycie RAM
            ram_usage = self.get_ram_usage()
            logger.debug(f"Aktualne zużycie RAM: {ram_usage}%")
            
            if ram_usage > MAX_RAM_PERCENT:
                logger.warning(f"Przekroczono limit RAM: {ram_usage}% > {MAX_RAM_PERCENT}%")
                
                # Czyszczenie kontenerów Docker
                self.clean_docker_containers()
                
                # Czyszczenie procesów zombie
                self.clean_zombie_processes()
                
                # Rotacja głównego pliku logu
                if os.path.exists(self.assistant_log):
                    self.limit_log_file_size(self.assistant_log)
            
            # Sprawdź zużycie dysku
            evopy_size = self.get_evopy_disk_usage()
            logger.debug(f"Rozmiar katalogu Evopy: {evopy_size / (1024*1024*1024):.2f} GB")
            
            if evopy_size > MAX_DISK_USAGE:
                logger.warning(f"Przekroczono limit dysku: {evopy_size / (1024*1024*1024):.2f} GB > {MAX_DISK_USAGE / (1024*1024*1024):.2f} GB")
                
                # Ograniczenie rozmiaru głównego pliku logu
                if os.path.exists(self.assistant_log):
                    self.limit_log_file_size(self.assistant_log)
                
                # Czyszczenie starych logów
                self.clean_old_logs()
            
            # Rotacja pliku logu monitora
            self.rotate_log_file(LOG_FILE)
            
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania zasobów: {e}")
    
    def run(self):
        """Uruchamia monitor zasobów w pętli"""
        logger.info("Rozpoczęcie monitorowania zasobów")
        
        while self.running:
            self.check_and_manage_resources()
            time.sleep(CHECK_INTERVAL)
        
        logger.info("Zakończenie monitorowania zasobów")


def format_bytes(bytes_value):
    """Formatuje bajty do czytelnej postaci"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def generate_report():
    """Generuje raport o stanie zasobów systemu"""
    # Informacje o systemie
    report = "=== RAPORT ZASOBÓW SYSTEMU ===\n\n"
    
    # Informacje o CPU
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    report += f"CPU:\n"
    for i, percent in enumerate(cpu_percent):
        report += f"  Rdzeń {i}: {percent}%\n"
    report += f"  Średnie użycie: {sum(cpu_percent) / len(cpu_percent):.1f}%\n\n"
    
    # Informacje o pamięci RAM
    memory = psutil.virtual_memory()
    report += f"Pamięć RAM:\n"
    report += f"  Całkowita: {format_bytes(memory.total)}\n"
    report += f"  Dostępna: {format_bytes(memory.available)}\n"
    report += f"  Używana: {format_bytes(memory.used)} ({memory.percent}%)\n\n"
    
    # Informacje o dysku
    report += f"Dysk:\n"
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            report += f"  {partition.mountpoint}:\n"
            report += f"    Całkowita: {format_bytes(usage.total)}\n"
            report += f"    Używana: {format_bytes(usage.used)} ({usage.percent}%)\n"
        except PermissionError:
            continue
    
    # Informacje o procesach
    report += "\nNajbardziej obciążające procesy:\n"
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
        try:
            # Aktualizuj informacje o CPU dla procesu
            proc.cpu_percent(interval=0.1)
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Poczekaj chwilę, aby zebrać dane o użyciu CPU
    time.sleep(0.5)
    
    # Zaktualizuj informacje o procesach
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
        try:
            for p in processes:
                if p['pid'] == proc.info['pid']:
                    p['cpu_percent'] = proc.info['cpu_percent']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sortuj procesy według zużycia CPU
    processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)
    
    # Wyświetl top 10 procesów
    for i, proc in enumerate(processes[:10], 1):
        report += f"  {i}. PID: {proc.get('pid', 'N/A')}, Nazwa: {proc.get('name', 'N/A')}, "
        report += f"CPU: {proc.get('cpu_percent', 0):.1f}%, RAM: {proc.get('memory_percent', 0):.1f}%\n"
    
    # Informacje o kontenerach Docker
    report += "\nKontenery Docker:\n"
    try:
        docker_ps = subprocess.run(['docker', 'ps', '--format', '{{.ID}}\t{{.Names}}\t{{.Status}}'], 
                                  capture_output=True, text=True, check=False)
        if docker_ps.returncode == 0 and docker_ps.stdout.strip():
            for line in docker_ps.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        container_id, name, status = parts[0], parts[1], parts[2]
                        report += f"  {name} ({container_id}): {status}\n"
        else:
            report += "  Brak działających kontenerów\n"
    except Exception as e:
        report += f"  Błąd podczas pobierania informacji o kontenerach: {e}\n"
    
    return report

def run_in_background():
    """Uruchamia monitor zasobów w tle"""
    # Przekierowanie standardowego wyjścia i błędów do pliku
    log_file = os.path.join(LOG_DIR, "monitor_daemon.log")
    
    # Uruchom monitor
    monitor = ResourceMonitor()
    monitor.run()

def main():
    """Główna funkcja"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor zasobów systemowych dla projektu Evopy")
    parser.add_argument("--background", action="store_true", help="Uruchom w tle")
    parser.add_argument("--check", action="store_true", help="Wykonaj jednorazowe sprawdzenie i wyjdź")
    parser.add_argument("--report", action="store_true", help="Generuj raport o stanie zasobów")
    args = parser.parse_args()
    
    if args.report:
        # Generuj i wyświetl raport o stanie zasobów
        print(generate_report())
    elif args.background:
        print("Uruchamianie monitora zasobów w tle...")
        run_in_background()
    elif args.check:
        print("Wykonywanie jednorazowego sprawdzenia zasobów...")
        monitor = ResourceMonitor()
        monitor.check_and_manage_resources()
    else:
        print("Uruchamianie monitora zasobów w trybie interaktywnym...")
        monitor = ResourceMonitor()
        monitor.run()


if __name__ == "__main__":
    main()

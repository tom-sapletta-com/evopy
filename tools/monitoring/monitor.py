#!/usr/bin/env python3
"""
debug_monitor.py - Monitor debugowania dla Ewolucyjnego Asystenta

Ten skrypt monitoruje działanie Ewolucyjnego Asystenta w czasie rzeczywistym,
zbiera informacje diagnostyczne i wyświetla je w interaktywnej konsoli.
Umożliwia również przechwytywanie i analizowanie komunikacji z modelem.

Uruchomienie:
python debug_monitor.py --script ./evo_assistant.py
"""

import os
import re
import sys
import json
import time
import fcntl
import errno
import argparse
import threading
import subprocess
import curses
import psutil
import docker
from datetime import datetime
from pathlib import Path

# Konfiguracja
DEFAULT_SCRIPT_PATH = "./evo_assistant.py"
LOG_DIR = Path("./debug_logs")
DOCKER_STATS_INTERVAL = 2  # w sekundach
MODEL_API_HOST = "http://localhost:11434"

# Upewnij się, że katalog logów istnieje
os.makedirs(LOG_DIR, exist_ok=True)

# Funkcje pomocnicze
def setup_logging():
    """Konfiguruje system logowania"""
    import logging
    
    log_file = LOG_DIR / f"debug_monitor_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    
    return logging.getLogger("debug-monitor")

def set_nonblocking(file_descriptor):
    """Ustawia deskryptor pliku w tryb nieblokujący"""
    flags = fcntl.fcntl(file_descriptor, fcntl.F_GETFL)
    fcntl.fcntl(file_descriptor, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def read_nonblocking(file_descriptor):
    """Odczytuje dane z deskryptora pliku w trybie nieblokującym"""
    try:
        return os.read(file_descriptor, 4096).decode('utf-8')
    except OSError as e:
        if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
            return ""
        else:
            raise

def capture_model_api_call(call_data):
    """Zapisuje przechwycone wywołanie API modelu do pliku"""
    calls_dir = LOG_DIR / "model_calls"
    os.makedirs(calls_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    call_file = calls_dir / f"call_{timestamp}.json"
    
    with open(call_file, 'w') as f:
        json.dump(call_data, f, indent=2)

def format_size(size_bytes):
    """Formatuje rozmiar w bajtach do czytelnej postaci"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f}MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f}GB"

def format_time(seconds):
    """Formatuje czas w sekundach do czytelnej postaci"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"

def get_active_docker_containers():
    """Pobiera listę aktywnych kontenerów Docker"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        return [
            {
                "id": container.id[:12],
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                "status": container.status,
                "created": container.attrs["Created"]
            }
            for container in containers
        ]
    except Exception as e:
        return [{"error": str(e)}]

def get_container_stats(container_id):
    """Pobiera statystyki kontenera Docker"""
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # Oblicz użycie CPU
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        num_cpus = stats["cpu_stats"]["online_cpus"]
        cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
        
        # Oblicz użycie pamięci
        memory_usage = stats["memory_stats"]["usage"]
        memory_limit = stats["memory_stats"]["limit"]
        memory_percent = (memory_usage / memory_limit) * 100.0
        
        return {
            "cpu_percent": cpu_percent,
            "memory_usage": memory_usage,
            "memory_limit": memory_limit,
            "memory_percent": memory_percent,
            "network_rx": stats["networks"]["eth0"]["rx_bytes"] if "networks" in stats else 0,
            "network_tx": stats["networks"]["eth0"]["tx_bytes"] if "networks" in stats else 0
        }
    except Exception as e:
        return {"error": str(e)}

def get_project_structure(evo_assistant_dir):
    """Pobiera strukturę katalogów projektu Ewolucyjnego Asystenta"""
    if not os.path.exists(evo_assistant_dir):
        return {"error": f"Katalog {evo_assistant_dir} nie istnieje"}
    
    structure = {"name": os.path.basename(evo_assistant_dir), "type": "directory", "children": []}
    
    for item in os.listdir(evo_assistant_dir):
        item_path = os.path.join(evo_assistant_dir, item)
        
        if os.path.isdir(item_path):
            structure["children"].append({"name": item, "type": "directory", "count": len(os.listdir(item_path))})
        else:
            structure["children"].append({"name": item, "type": "file", "size": os.path.getsize(item_path)})
    
    return structure

def monitor_process(pid):
    """Monitoruje proces o podanym PID i zwraca informacje o jego zasobach"""
    try:
        process = psutil.Process(pid)
        memory_info = process.memory_info()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "threads": process.num_threads(),
            "status": process.status(),
            "running_time": time.time() - process.create_time()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

class DockerStatsCollector(threading.Thread):
    """Klasa do zbierania statystyk Docker w tle"""
    
    def __init__(self, update_interval=DOCKER_STATS_INTERVAL):
        super().__init__()
        self.update_interval = update_interval
        self.containers = []
        self.stats = {}
        self.running = True
        self.daemon = True  # Wątek zostanie automatycznie zakończony, gdy główny program zakończy działanie
    
    def run(self):
        while self.running:
            self.containers = get_active_docker_containers()
            
            for container in self.containers:
                container_id = container["id"]
                self.stats[container_id] = get_container_stats(container_id)
            
            time.sleep(self.update_interval)
    
    def stop(self):
        self.running = False

class ModelCallsInterceptor(threading.Thread):
    """Klasa do przechwytywania wywołań API modelu"""
    
    def __init__(self, host=MODEL_API_HOST):
        super().__init__()
        self.host = host
        self.running = True
        self.daemon = True
        self.calls = []
    
    def run(self):
        try:
            import pyshark
            
            # Przypisz odpowiedni interfejs sieciowy
            interface = "lo" if sys.platform == "linux" else "loopback" if sys.platform == "darwin" else "\\Device\\NPF_Loopback"
            
            # Uruchom przechwytywanie pakietów HTTP na porcie 11434
            capture = pyshark.LiveCapture(interface=interface, display_filter="tcp port 11434")
            
            for packet in capture.sniff_continuously():
                if not self.running:
                    break
                
                try:
                    if hasattr(packet, 'http') and hasattr(packet.http, 'request_method'):
                        if packet.http.request_method == 'POST':
                            if 'api/chat' in packet.http.request_uri or 'api/generate' in packet.http.request_uri:
                                # Pobierz zawartość zapytania
                                request_body = packet.http.file_data if hasattr(packet.http, 'file_data') else ""
                                
                                try:
                                    request_data = json.loads(request_body)
                                    
                                    call_data = {
                                        "timestamp": datetime.now().isoformat(),
                                        "endpoint": packet.http.request_uri,
                                        "method": packet.http.request_method,
                                        "request": request_data
                                    }
                                    
                                    self.calls.append(call_data)
                                    capture_model_api_call(call_data)
                                except:
                                    pass
                except:
                    continue
        
        except ImportError:
            # Jeśli pyshark nie jest zainstalowany, próbuj używać tcpdump
            try:
                if sys.platform == "linux" or sys.platform == "darwin":
                    process = subprocess.Popen(
                        ["tcpdump", "-i", "lo", "-A", "-s", "0", "tcp", "port", "11434"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    # Ignoruj stderr
                    set_nonblocking(process.stderr.fileno())
                    
                    # Przetwarzaj stdout
                    current_request = ""
                    capturing = False
                    
                    while self.running:
                        line = process.stdout.readline().decode('utf-8', errors='ignore')
                        if not line:
                            time.sleep(0.1)
                            continue
                        
                        # Wykryj początek zapytania POST
                        if "POST /api/chat" in line or "POST /api/generate" in line:
                            current_request = line
                            capturing = True
                        elif capturing and line.strip() == "":
                            capturing = False
                            
                            # Przetwórz przechwycone zapytanie
                            try:
                                # Spróbuj znaleźć dane JSON w przechwyconym tekście
                                match = re.search(r'(\{.*\})', current_request, re.DOTALL)
                                if match:
                                    request_body = match.group(1)
                                    request_data = json.loads(request_body)
                                    
                                    call_data = {
                                        "timestamp": datetime.now().isoformat(),
                                        "endpoint": "/api/chat" if "POST /api/chat" in current_request else "/api/generate",
                                        "method": "POST",
                                        "request": request_data
                                    }
                                    
                                    self.calls.append(call_data)
                                    capture_model_api_call(call_data)
                            except:
                                pass
                            
                            current_request = ""
                        elif capturing:
                            current_request += line
            
            except:
                pass
    
    def stop(self):
        self.running = False

class DebugMonitor:
    """Główna klasa monitora debugowania"""
    
    def __init__(self, script_path):
        self.logger = setup_logging()
        self.script_path = script_path
        self.process = None
        self.stdout_buffer = ""
        self.stderr_buffer = ""
        self.docker_stats = DockerStatsCollector()
        self.model_interceptor = ModelCallsInterceptor()
        self.exit_flag = False
        
        # Inicjalizacja kursorów do wyświetlania w trybie TUI
        self.main_win = None
        self.process_win = None
        self.docker_win = None
        self.logs_win = None
        self.model_win = None
        self.status_win = None
        
        # Dane monitorowania
        self.process_stats = {}
        self.start_time = None
        self.assistant_home_dir = os.path.expanduser("~/.evo-assistant")
    
    def start_assistant(self):
        """Uruchamia proces Ewolucyjnego Asystenta i rozpoczyna monitorowanie"""
        self.logger.info(f"Uruchamianie asystenta z pliku: {self.script_path}")
        
        # Uruchom proces asystenta
        self.process = subprocess.Popen(
            ["python", self.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=0  # Bez buforowania
        )
        
        self.start_time = time.time()
        
        # Ustaw deskryptory plików w tryb nieblokujący
        set_nonblocking(self.process.stdout.fileno())
        set_nonblocking(self.process.stderr.fileno())
        
        # Uruchom wątki monitorujące
        self.docker_stats.start()
        self.model_interceptor.start()
        
        self.logger.info(f"Asystent uruchomiony z PID: {self.process.pid}")
    
    def stop(self):
        """Zatrzymuje monitorowanie i zamyka proces asystenta"""
        self.exit_flag = True
        
        # Zatrzymaj wątki monitorujące
        self.docker_stats.stop()
        self.model_interceptor.stop()
        
        if self.process:
            self.logger.info("Zatrzymywanie procesu asystenta...")
            
            # Wyślij sygnał SIGTERM
            self.process.terminate()
            
            try:
                # Poczekaj na zakończenie procesu (maksymalnie 5 sekund)
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.logger.warning("Proces asystenta nie odpowiada. Wymuszanie zakończenia...")
                self.process.kill()
            
            self.logger.info("Proces asystenta zakończony")
    
    def read_process_output(self):
        """Odczytuje dane wyjściowe z procesu asystenta"""
        if not self.process:
            return
        
        # Odczytaj dane z stdout
        stdout_data = read_nonblocking(self.process.stdout.fileno())
        if stdout_data:
            self.stdout_buffer += stdout_data
            self.logger.debug(f"Stdout: {stdout_data}")
        
        # Odczytaj dane z stderr
        stderr_data = read_nonblocking(self.process.stderr.fileno())
        if stderr_data:
            self.stderr_buffer += stderr_data
            self.logger.warning(f"Stderr: {stderr_data}")
        
        # Sprawdź czy proces nadal działa
        if self.process.poll() is not None:
            self.logger.info(f"Proces asystenta zakończył działanie z kodem: {self.process.returncode}")
            
            # Odczytaj pozostałe dane
            stdout_data, stderr_data = self.process.communicate()
            if stdout_data:
                self.stdout_buffer += stdout_data.decode('utf-8')
            if stderr_data:
                self.stderr_buffer += stderr_data.decode('utf-8')
            
            self.process = None
    
    def update_process_stats(self):
        """Aktualizuje statystyki procesu"""
        if not self.process:
            return
        
        self.process_stats = monitor_process(self.process.pid)
    
    def send_input(self, input_text):
        """Wysyła dane wejściowe do procesu asystenta"""
        if not self.process:
            return False
        
        try:
            self.process.stdin.write(f"{input_text}\n".encode('utf-8'))
            self.process.stdin.flush()
            return True
        except:
            return False
    
    def run_tui(self):
        """Uruchamia interaktywny interfejs tekstowy (TUI)"""
        try:
            # Inicjalizacja curses
            curses.wrapper(self._run_tui_internal)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def _run_tui_internal(self, stdscr):
        """Wewnętrzna funkcja do obsługi TUI z curses"""
        # Konfiguracja curses
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)    # Normalny tekst
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Sukces/OK
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Ostrzeżenie
        curses.init_pair(4, curses.COLOR_RED, -1)      # Błąd
        curses.init_pair(5, curses.COLOR_CYAN, -1)     # Informacja
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Odwrócone kolory
        
        stdscr.clear()
        stdscr.refresh()
        stdscr.nodelay(True)  # Tryb nieblokujący dla getch()
        
        # Podziel ekran na sekcje
        height, width = stdscr.getmaxyx()
        
        # Okno statusu (górna belka)
        self.status_win = curses.newwin(1, width, 0, 0)
        self.status_win.bkgd(' ', curses.color_pair(6))
        
        # Okno procesu (lewy górny róg)
        self.process_win = curses.newwin(10, width // 2, 1, 0)
        
        # Okno Docker (prawy górny róg)
        self.docker_win = curses.newwin(10, width // 2, 1, width // 2)
        
        # Okno logów (lewy dolny róg)
        self.logs_win = curses.newwin(height - 11, width // 2, 11, 0)
        
        # Okno modelu (prawy dolny róg)
        self.model_win = curses.newwin(height - 11, width // 2, 11, width // 2)
        
        # Uruchom asystenta
        self.start_assistant()
        
        # Główna pętla
        input_buffer = ""
        cursor_position = 0
        
        while not self.exit_flag:
            try:
                # Aktualizacja danych
                self.read_process_output()
                self.update_process_stats()
                
                # Aktualizacja interfejsu
                self._update_status_win()
                self._update_process_win()
                self._update_docker_win()
                self._update_logs_win()
                self._update_model_win()
                
                # Rysowanie paska wejściowego
                stdscr.move(height - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(height - 1, 0, "> " + input_buffer, curses.color_pair(1))
                stdscr.move(height - 1, 2 + cursor_position)
                
                # Odśwież wszystkie okna
                stdscr.noutrefresh()
                self.status_win.noutrefresh()
                self.process_win.noutrefresh()
                self.docker_win.noutrefresh()
                self.logs_win.noutrefresh()
                self.model_win.noutrefresh()
                curses.doupdate()
                
                # Obsługa wejścia użytkownika
                c = stdscr.getch()
                if c != -1:
                    if c == ord('q'):  # Wyjście
                        self.exit_flag = True
                    elif c == curses.KEY_ENTER or c == 10 or c == 13:  # Enter
                        if input_buffer:
                            # Wyślij dane do asystenta
                            self.send_input(input_buffer)
                            input_buffer = ""
                            cursor_position = 0
                    elif c == curses.KEY_BACKSPACE or c == 127:  # Backspace
                        if cursor_position > 0:
                            input_buffer = input_buffer[:cursor_position-1] + input_buffer[cursor_position:]
                            cursor_position -= 1
                    elif c == curses.KEY_LEFT:  # Strzałka w lewo
                        if cursor_position > 0:
                            cursor_position -= 1
                    elif c == curses.KEY_RIGHT:  # Strzałka w prawo
                        if cursor_position < len(input_buffer):
                            cursor_position += 1
                    elif 32 <= c <= 126:  # Zwykłe znaki
                        input_buffer = input_buffer[:cursor_position] + chr(c) + input_buffer[cursor_position:]
                        cursor_position += 1
                
                # Krótkie opóźnienie
                time.sleep(0.05)
            
            except KeyboardInterrupt:
                self.exit_flag = True
            except:
                # Ignoruj inne wyjątki w pętli głównej
                pass
    
    def _update_status_win(self):
        """Aktualizuje okno statusu"""
        self.status_win.clear()
        
        # Status asystenta
        status_text = "URUCHOMIONY" if self.process else "ZATRZYMANY"
        status_color = curses.color_pair(2) if self.process else curses.color_pair(4)
        
        # Czas działania
        running_time = format_time(time.time() - self.start_time) if self.start_time else "0s"
        
        # Liczba kontenerów Docker
        containers_count = len(self.docker_stats.containers)
        
        # Liczba wywołań modelu
        model_calls_count = len(self.model_interceptor.calls)
        
        # Wyświetl informacje statusu
        width = self.status_win.getmaxyx()[1]
        status_line = f" Monitor Debugowania | Status: {status_text} | Czas: {running_time} | Kontenery: {containers_count} | Wywołania modelu: {model_calls_count} | q - Wyjście"
        
        if len(status_line) > width:
            status_line = status_line[:width-3] + "..."
        
        self.status_win.addstr(0, 0, status_line, curses.color_pair(6))
        self.status_win.refresh()
    
    def _update_process_win(self):
        """Aktualizuje okno procesu"""
        self.process_win.clear()
        self.process_win.box()
        self.process_win.addstr(0, 2, "Proces Asystenta", curses.color_pair(5) | curses.A_BOLD)
        
        if self.process_stats:
            # PID i status
            self.process_win.addstr(1, 2, f"PID: {self.process.pid} | Status: {self.process_stats.get('status', 'N/A')}")
            
            # Użycie CPU
            cpu_percent = self.process_stats.get('cpu_percent', 0)
            cpu_color = curses.color_pair(2) if cpu_percent < 50 else curses.color_pair(3) if cpu_percent < 80 else curses.color_pair(4)
            self.process_win.addstr(2, 2, f"CPU: {cpu_percent:.2f}%", cpu_color)
            
            # Pamięć
            memory_rss = self.process_stats.get('memory_rss', 0)
            memory_vms = self.process_stats.get('memory_vms', 0)
            self.process_win.addstr(3, 2, f"Pamięć: RSS {format_size(memory_rss)} | VMS {format_size(memory_vms)}")
            
            # Wątki
            self.process_win.addstr(4, 2, f"Wątki: {self.process_stats.get('threads', 0)}")
            
            # Czas działania
            running_time = self.process_stats.get('running_time', 0)
            self.process_win.addstr(5, 2, f"Czas działania: {format_time(running_time)}")
        
        else:
            self.process_win.addstr(1, 2, "Brak danych procesu", curses.color_pair(3))
        
        # Struktura katalogów projektu
        self.process_win.addstr(7, 2, "Struktura projektu:", curses.color_pair(5))
        
        structure = get_project_structure(self.assistant_home_dir)
        if "error" in structure:
            self.process_win.addstr(8, 2, structure["error"], curses.color_pair(3))
        else:
            for i, child in enumerate(structure.get("children", []), 1):
                if i > 2:  # Ogranicz do dwóch pozycji
                    break
                
                if child["type"] == "directory":
                    self.process_win.addstr(7+i, 2, f"{child['name']}/: {child['count']} elementów")
                else:
                    self.process_win.addstr(7+i, 2, f"{child['name']}: {format_size(child['size'])}")
        
        self.process_win.refresh()
    
    def _update_docker_win(self):
        """Aktualizuje okno Docker"""
        self.docker_win.clear()
        self.docker_win.box()
        self.docker_win.addstr(0, 2, "Kontenery Docker", curses.color_pair(5) | curses.A_BOLD)
        
        containers = self.docker_stats.containers
        if not containers:
            self.docker_win.addstr(1, 2, "Brak aktywnych kontenerów", curses.color_pair(3))
        else:
            # Nagłówek tabeli
            self.docker_win.addstr(1, 2, "ID  | Nazwa | Obraz | Status", curses.color_pair(5))
            
            # Lista kontenerów
            for i, container in enumerate(containers[:5], 2):  # Ogranicz do 5 kontenerów
                if i >= 8:  # Ogranicz do wysokości okna
                    break
                
                container_id = container.get("id", "N/A")[:8]
                container_name = container.get("name", "N/A")
                container_image = container.get("image", "N/A").split(":")[-2].split("/")[-1] if ":" in container.get("image", "N/A") else container.get("image", "N/A")
                container_status = container.get("status", "N/A")
                
                status_color = curses.color_pair(2) if container_status == "running" else curses.color_pair(3)
                
                try:
                    self.docker_win.addstr(i, 2, f"{container_id[:8]} | ", curses.color_pair(1))
                    self.docker_win.addstr(f"{container_name[:10]} | ", curses.color_pair(1))
                    self.docker_win.addstr(f"{container_image[:10]} | ", curses.color_pair(1))
                    self.docker_win.addstr(f"{container_status}", status_color)
                    
                    # Jeśli mamy statystyki dla tego kontenera
                    if container_id in self.docker_stats.stats:
                        stats = self.docker_stats.stats[container_id]
                        if "error" not in stats:
                            cpu = stats.get("cpu_percent", 0)
                            memory = stats.get("memory_percent", 0)
                            
                            cpu_color = curses.color_pair(2) if cpu < 50 else curses.color_pair(3) if cpu < 80 else curses.color_pair(4)
                            memory_color = curses.color_pair(2) if memory < 50 else curses.color_pair(3) if memory < 80 else curses.color_pair(4)
                            
                            self.docker_win.addstr(i, 45, f"CPU: ", curses.color_pair(1))
                            self.docker_win.addstr(f"{cpu:.1f}%", cpu_color)
                            self.docker_win.addstr(f" | RAM: ", curses.color_pair(1))
                            self.docker_win.addstr(f"{memory:.1f}%", memory_color)
                except:
                    pass
        
        self.docker_win.refresh()
    
    def _update_logs_win(self):
        """Aktualizuje okno logów"""
        self.logs_win.clear()
        self.logs_win.box()
        self.logs_win.addstr(0, 2, "Logi Asystenta", curses.color_pair(5) | curses.A_BOLD)
        
        # Oblicz maksymalną liczbę wierszy do wyświetlenia
        max_rows = self.logs_win.getmaxyx()[0] - 2
        max_cols = self.logs_win.getmaxyx()[1] - 4
        
        # Podziel bufor stdout na linie i wyświetl ostatnie N linii
        stdout_lines = self.stdout_buffer.split("\n")
        if len(stdout_lines) > max_rows:
            stdout_lines = stdout_lines[-max_rows:]
        
        for i, line in enumerate(stdout_lines, 1):
            if i >= max_rows:
                break
            
            # Ogranicz długość linii
            if len(line) > max_cols:
                line = line[:max_cols-3] + "..."
            
            # Wybierz kolor w zależności od zawartości
            if "ERROR" in line or "Błąd" in line:
                color = curses.color_pair(4)
            elif "WARNING" in line or "Ostrzeżenie" in line:
                color = curses.color_pair(3)
            elif "INFO" in line or "Informacja" in line:
                color = curses.color_pair(5)
            else:
                color = curses.color_pair(1)
            
            try:
                self.logs_win.addstr(i, 2, line, color)
            except:
                pass
        
        self.logs_win.refresh()
    
    def _update_model_win(self):
        """Aktualizuje okno modelu"""
        self.model_win.clear()
        self.model_win.box()
        self.model_win.addstr(0, 2, "Wywołania Modelu", curses.color_pair(5) | curses.A_BOLD)
        
        # Oblicz maksymalną liczbę wierszy do wyświetlenia
        max_rows = self.model_win.getmaxyx()[0] - 2
        max_cols = self.model_win.getmaxyx()[1] - 4
        
        calls = self.model_interceptor.calls
        if not calls:
            self.model_win.addstr(1, 2, "Brak przechwyconych wywołań modelu", curses.color_pair(3))
        else:
            # Wyświetl ostatnie N wywołań
            displayed_calls = calls[-max_rows+1:]
            
            for i, call in enumerate(displayed_calls, 1):
                if i >= max_rows:
                    break
                
                timestamp = datetime.fromisoformat(call.get("timestamp", "")).strftime("%H:%M:%S")
                endpoint = call.get("endpoint", "").split("/")[-1]
                
                try:
                    self.model_win.addstr(i, 2, f"{timestamp} - {endpoint}", curses.color_pair(5))
                    
                    # Wyświetl fragment zapytania
                    request = call.get("request", {})
                    if "messages" in request:
                        messages = request["messages"]
                        if messages and len(messages) > 0:
                            last_message = messages[-1]
                            content = last_message.get("content", "")
                            
                            if len(content) > max_cols - 15:
                                content = content[:max_cols-18] + "..."
                            
                            self.model_win.addstr(i+1, 4, f"> {content}", curses.color_pair(1))
                    elif "prompt" in request:
                        prompt = request["prompt"]
                        if len(prompt) > max_cols - 10:
                            prompt = prompt[:max_cols-13] + "..."
                        
                        self.model_win.addstr(i+1, 4, f"> {prompt}", curses.color_pair(1))
                except:
                    pass
        
        self.model_win.refresh()

def main():
    parser = argparse.ArgumentParser(description="Monitor debugowania dla Ewolucyjnego Asystenta")
    parser.add_argument("--script", type=str, default=DEFAULT_SCRIPT_PATH, help="Ścieżka do skryptu asystenta")
    args = parser.parse_args()
    
    monitor = DebugMonitor(args.script)
    
    try:
        monitor.run_tui()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
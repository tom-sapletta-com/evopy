#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
import datetime
import time
import glob

# Konfiguracja logowania
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f'run_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('run-script')

def check_requirements():
    """Sprawdza, czy wymagania są zainstalowane"""
    logger.info("Sprawdzanie wymagań...")
    try:
        # Sprawdź, czy Flask jest zainstalowany
        import flask
        logger.info(f"Flask jest zainstalowany (wersja {flask.__version__})")
        return True
    except ImportError:
        logger.error("Flask nie jest zainstalowany. Instalowanie...")
        try:
            requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
            if os.path.exists(requirements_file):
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                    check=True,
                    capture_output=True
                )
                logger.info("Wymagania zostały zainstalowane")
                return True
            else:
                logger.warning("Plik requirements.txt nie istnieje, instalowanie Flask...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "flask==2.0.1", "werkzeug==2.0.0"],
                    check=True,
                    capture_output=True
                )
                logger.info("Flask został zainstalowany")
                return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas instalacji wymagań: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
            return False

def find_server_file():
    """Znajduje plik serwera (server.*)"""
    server_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Najpierw sprawdź server.py
    server_py = os.path.join(server_dir, 'server.py')
    if os.path.exists(server_py):
        return server_py
    
    # Jeśli nie ma server.py, znajdź dowolny plik server.*
    server_files = glob.glob(os.path.join(server_dir, 'server.*'))
    if server_files:
        return server_files[0]
    
    return None

def run_server():
    """Uruchamia serwer"""
    logger.info("Uruchamianie serwera...")
    
    # Znajdź plik serwera
    server_path = find_server_file()
    if not server_path:
        logger.error("Nie znaleziono pliku serwera (server.*)")
        return False
    
    logger.info(f"Znaleziono plik serwera: {server_path}")
    
    try:
        # Określ sposób uruchomienia na podstawie rozszerzenia pliku
        file_ext = os.path.splitext(server_path)[1].lower()
        
        if file_ext == '.py':
            cmd = [sys.executable, server_path]
        elif file_ext == '.js':
            cmd = ['node', server_path]
        elif file_ext == '.sh':
            cmd = ['bash', server_path]
        else:
            logger.error(f"Nieobsługiwane rozszerzenie pliku: {file_ext}")
            return False
        
        # Uruchom serwer
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        logger.info(f"Serwer uruchomiony (PID: {process.pid})")
        logger.info("Serwer dostępny pod adresem: http://localhost:5000")
        
        # Monitoruj logi serwera
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                logger.info(f"[SERVER] {line.strip()}")
        
        # Sprawdź kod wyjścia
        exit_code = process.poll()
        if exit_code != 0:
            logger.error(f"Serwer zakończył działanie z kodem błędu: {exit_code}")
            return False
        
        logger.info("Serwer zakończył działanie")
        return True
    
    except KeyboardInterrupt:
        logger.info("Otrzymano sygnał przerwania. Zatrzymywanie serwera...")
        if 'process' in locals():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        logger.info("Serwer zatrzymany")
        return True
    
    except Exception as e:
        logger.error(f"Wystąpił błąd podczas uruchamiania serwera: {str(e)}")
        return False

def main():
    """Główna funkcja programu"""
    logger.info("Uruchamianie skryptu run.py")
    
    # Sprawdź wymagania
    if not check_requirements():
        logger.error("Nie można uruchomić serwera z powodu braku wymagań")
        return 1
    
    # Uruchom serwer
    if not run_server():
        logger.error("Wystąpił błąd podczas uruchamiania serwera")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
import datetime
import time

# Konfiguracja logowania
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f'run_server_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('run-server')

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
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                capture_output=True
            )
            logger.info("Wymagania zostały zainstalowane")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas instalacji wymagań: {e.stderr.decode()}")
            return False

def run_server():
    """Uruchamia serwer Flask"""
    logger.info("Uruchamianie serwera...")
    
    # Znajdź plik serwera (server.py lub inny plik server.*)
    server_dir = os.path.dirname(os.path.abspath(__file__))
    server_files = [f for f in os.listdir(server_dir) if f.startswith('server.') and os.path.isfile(os.path.join(server_dir, f))]
    
    # Priorytetyzuj server.py, jeśli istnieje
    if 'server.py' in server_files:
        server_path = os.path.join(server_dir, 'server.py')
    elif server_files:
        server_path = os.path.join(server_dir, server_files[0])
    else:
        server_path = os.path.join(server_dir, 'server.py')  # Domyślnie
    if not os.path.exists(server_path):
        logger.error(f"Plik serwera nie istnieje: {server_path}")
        return False
    
    try:
        # Uruchom serwer
        process = subprocess.Popen(
            [sys.executable, server_path],
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
    logger.info("Uruchamianie skryptu run_server.py")
    
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import logging
import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Konfiguracja logowania
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f'server_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('converters-server')

app = Flask(__name__)

# Ścieżka do katalogu z modułami
MODULES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONVERTERS_DIR = os.path.join(MODULES_DIR, "converters")

@app.route('/')
def index():
    """Strona główna z listą modułów konwersji"""
    logger.info("Dostęp do strony głównej")
    modules = []
    
    # Lista modułów konwersji
    converters = [
        {"name": "text2python", "description": "Konwersja tekstu na kod Python"},
        {"name": "python2text", "description": "Konwersja kodu Python na opis tekstowy"},
        {"name": "text2shell", "description": "Konwersja tekstu na polecenia shell"},
        {"name": "shell2text", "description": "Konwersja poleceń shell na opis tekstowy"},
        {"name": "text2sql", "description": "Konwersja tekstu na zapytania SQL"},
        {"name": "sql2text", "description": "Konwersja zapytań SQL na opis tekstowy"},
        {"name": "text2regex", "description": "Konwersja tekstu na wyrażenia regularne"},
        {"name": "regex2text", "description": "Konwersja wyrażeń regularnych na opis tekstowy"}
    ]
    
    return render_template('index.html', converters=converters)

@app.route('/docker')
def docker_containers():
    """Strona z listą kontenerów Docker"""
    logger.info("Dostęp do strony z kontenerami Docker")
    try:
        # Uruchom polecenie docker ps w celu uzyskania listy kontenerów
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    containers.append({
                        "id": parts[0],
                        "image": parts[1],
                        "status": parts[2],
                        "name": parts[3]
                    })
        
        return render_template('docker.html', containers=containers)
    except subprocess.CalledProcessError as e:
        error_message = f"Błąd podczas pobierania listy kontenerów Docker: {e.stderr}"
        return render_template('docker.html', error=error_message, containers=[])
    except Exception as e:
        error_message = f"Wystąpił nieoczekiwany błąd: {str(e)}"
        return render_template('docker.html', error=error_message, containers=[])

@app.route('/module/<string:name>')
def module_details(name):
    """Szczegóły modułu konwersji"""
    logger.info(f"Dostęp do szczegółów modułu: {name}")
    module_path = os.path.join(CONVERTERS_DIR, f"{name}.py")
    
    if not os.path.exists(module_path):
        return "Moduł nie istnieje", 404
    
    # Odczytaj zawartość pliku modułu
    with open(module_path, 'r') as f:
        content = f.read()
    
    return render_template('module.html', name=name, content=content)

@app.route('/docker/run', methods=['POST'])
def docker_run():
    """Uruchamia polecenie Docker"""
    command = request.form.get('command', '')
    logger.info(f"Uruchamianie polecenia Docker: {command}")
    
    if not command:
        return jsonify({"error": "Brak polecenia"}), 400
    
    try:
        # Uruchom polecenie Docker
        result = subprocess.run(
            ["docker"] + command.split(),
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Utwórz katalog templates, jeśli nie istnieje
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

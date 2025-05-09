#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service Template - Szablon do generowania serwisów webowych z kodu Python

Ten moduł służy jako szablon do tworzenia serwisów webowych z kodu Python
generowanego przez Evopy. Zapewnia dekoratory i narzędzia do łatwego
tworzenia API i interfejsów webowych.
"""

import os
import sys
import json
import time
import inspect
import logging
import traceback
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Callable

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("evopy-service")

try:
    from flask import Flask, request, jsonify, render_template, send_from_directory
except ImportError:
    logger.error("Flask nie jest zainstalowany. Instaluję...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, request, jsonify, render_template, send_from_directory

# Globalne zmienne
app = Flask(__name__)
SERVICE_INFO = {
    "name": "Evopy Service",
    "description": "Serwis wygenerowany przez Evopy",
    "version": "1.0.0",
    "endpoints": [],
    "functions": {},
    "ui_enabled": True
}

# Katalogi dla szablonów i plików statycznych
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Utwórz katalogi, jeśli nie istnieją
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Utwórz podstawowy szablon HTML
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ service.name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 20px; }
        .endpoint-card { margin-bottom: 20px; }
        .response-area { min-height: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <header class="mb-4">
            <h1>{{ service.name }}</h1>
            <p class="lead">{{ service.description }}</p>
            <p><small>Wersja: {{ service.version }}</small></p>
        </header>

        <div class="row">
            <div class="col-md-12">
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        Dostępne endpointy
                    </div>
                    <div class="card-body">
                        {% for endpoint in service.endpoints %}
                        <div class="endpoint-card card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span>
                                    <span class="badge bg-{{ endpoint.method_color }}">{{ endpoint.method }}</span>
                                    <code>{{ endpoint.path }}</code>
                                </span>
                                <span>{{ endpoint.description }}</span>
                            </div>
                            <div class="card-body">
                                <form class="api-form" data-endpoint="{{ endpoint.path }}" data-method="{{ endpoint.method }}">
                                    {% if endpoint.params %}
                                    <h6>Parametry:</h6>
                                    <div class="mb-3">
                                        {% for param in endpoint.params %}
                                        <div class="mb-2">
                                            <label for="{{ endpoint.path }}-{{ param.name }}" class="form-label">
                                                {{ param.name }}
                                                {% if param.required %}
                                                <span class="text-danger">*</span>
                                                {% endif %}
                                            </label>
                                            <input type="{{ param.type }}" class="form-control" id="{{ endpoint.path }}-{{ param.name }}" 
                                                name="{{ param.name }}" placeholder="{{ param.description }}"
                                                {% if param.required %}required{% endif %}>
                                        </div>
                                        {% endfor %}
                                    </div>
                                    {% endif %}
                                    
                                    <div class="d-flex justify-content-between">
                                        <button type="submit" class="btn btn-primary">Wykonaj</button>
                                        <button type="button" class="btn btn-outline-secondary copy-curl-btn" 
                                            data-endpoint="{{ endpoint.path }}" data-method="{{ endpoint.method }}">
                                            Kopiuj jako cURL
                                        </button>
                                    </div>
                                    
                                    <div class="mt-3">
                                        <label class="form-label">Odpowiedź:</label>
                                        <div class="response-area border rounded p-3 bg-light">
                                            <pre class="response-content mb-0"></pre>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Obsługa formularzy API
            document.querySelectorAll('.api-form').forEach(form => {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const endpoint = this.dataset.endpoint;
                    const method = this.dataset.method;
                    const responseArea = this.querySelector('.response-content');
                    
                    // Zbierz dane z formularza
                    const formData = new FormData(this);
                    const data = {};
                    formData.forEach((value, key) => {
                        data[key] = value;
                    });
                    
                    // Przygotuj opcje fetch
                    const options = {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    };
                    
                    // Dodaj body dla metod innych niż GET
                    if (method !== 'GET') {
                        options.body = JSON.stringify(data);
                    }
                    
                    // Wykonaj zapytanie
                    let url = endpoint;
                    if (method === 'GET' && Object.keys(data).length > 0) {
                        const params = new URLSearchParams();
                        Object.entries(data).forEach(([key, value]) => {
                            params.append(key, value);
                        });
                        url += '?' + params.toString();
                    }
                    
                    responseArea.textContent = 'Ładowanie...';
                    
                    fetch(url, options)
                        .then(response => response.json())
                        .then(data => {
                            responseArea.textContent = JSON.stringify(data, null, 2);
                        })
                        .catch(error => {
                            responseArea.textContent = 'Błąd: ' + error.message;
                        });
                });
            });
            
            // Obsługa przycisków do kopiowania cURL
            document.querySelectorAll('.copy-curl-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const endpoint = this.dataset.endpoint;
                    const method = this.dataset.method;
                    const form = document.querySelector(`.api-form[data-endpoint="${endpoint}"][data-method="${method}"]`);
                    
                    // Zbierz dane z formularza
                    const formData = new FormData(form);
                    const data = {};
                    formData.forEach((value, key) => {
                        data[key] = value;
                    });
                    
                    // Utwórz komendę cURL
                    let curlCmd = `curl -X ${method} `;
                    
                    // Dodaj nagłówki
                    curlCmd += '-H "Content-Type: application/json" ';
                    
                    // Dodaj body dla metod innych niż GET
                    if (method !== 'GET' && Object.keys(data).length > 0) {
                        curlCmd += `-d '${JSON.stringify(data)}' `;
                    }
                    
                    // Dodaj URL
                    let url = window.location.origin + endpoint;
                    if (method === 'GET' && Object.keys(data).length > 0) {
                        const params = new URLSearchParams();
                        Object.entries(data).forEach(([key, value]) => {
                            params.append(key, value);
                        });
                        url += '?' + params.toString();
                    }
                    curlCmd += url;
                    
                    // Kopiuj do schowka
                    navigator.clipboard.writeText(curlCmd)
                        .then(() => {
                            alert('Skopiowano komendę cURL do schowka!');
                        })
                        .catch(err => {
                            console.error('Nie udało się skopiować: ', err);
                        });
                });
            });
        });
    </script>
</body>
</html>
"""

# Zapisz szablon HTML
with open(os.path.join(TEMPLATE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(INDEX_TEMPLATE)

# Dekoratory dla endpointów API
def api_endpoint(path: str, methods: List[str] = ["GET"], description: str = "", ui: bool = True):
    """
    Dekorator do tworzenia endpointów API
    
    Args:
        path: Ścieżka endpointu (np. "/api/hello")
        methods: Lista dozwolonych metod HTTP
        description: Opis endpointu
        ui: Czy endpoint ma być widoczny w interfejsie użytkownika
    """
    def decorator(func):
        endpoint_info = {
            "path": path,
            "method": methods[0],  # Pierwsza metoda jako domyślna dla UI
            "method_color": "success" if methods[0] == "GET" else "primary",
            "description": description,
            "params": []
        }
        
        # Pobierz informacje o parametrach funkcji
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name != "self":
                param_info = {
                    "name": param_name,
                    "type": "text",
                    "description": "",
                    "required": param.default == inspect.Parameter.empty
                }
                endpoint_info["params"].append(param_info)
        
        # Dodaj endpoint do listy
        if ui:
            SERVICE_INFO["endpoints"].append(endpoint_info)
        
        # Zapisz funkcję
        SERVICE_INFO["functions"][path] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Pobierz parametry z żądania
                if request.method == "GET":
                    params = request.args.to_dict()
                else:
                    params = request.json if request.is_json else request.form.to_dict()
                
                # Wywołaj funkcję z parametrami
                result = func(**params)
                
                # Zwróć wynik jako JSON
                return jsonify(result)
            except Exception as e:
                logger.error(f"Błąd podczas wykonywania endpointu {path}: {e}")
                return jsonify({
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
        
        # Zarejestruj endpoint w aplikacji Flask
        app.route(path, methods=methods)(wrapper)
        
        return func
    
    return decorator

def web_page(path: str, template: str = None, description: str = ""):
    """
    Dekorator do tworzenia stron webowych
    
    Args:
        path: Ścieżka strony (np. "/hello")
        template: Nazwa szablonu HTML
        description: Opis strony
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Wywołaj funkcję
                result = func(*args, **kwargs)
                
                # Jeśli wynik jest słownikiem, użyj go jako kontekstu dla szablonu
                if isinstance(result, dict):
                    if template:
                        return render_template(template, **result)
                    else:
                        return jsonify(result)
                
                # W przeciwnym razie zwróć wynik bezpośrednio
                return result
            except Exception as e:
                logger.error(f"Błąd podczas renderowania strony {path}: {e}")
                return jsonify({
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
        
        # Zarejestruj stronę w aplikacji Flask
        app.route(path)(wrapper)
        
        return func
    
    return decorator

# Domyślne endpointy
@app.route('/')
def index():
    """Strona główna z dokumentacją API"""
    return render_template('index.html', service=SERVICE_INFO)

@app.route('/api/info')
def api_info():
    """Informacje o serwisie"""
    return jsonify(SERVICE_INFO)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serwowanie plików statycznych"""
    return send_from_directory(STATIC_DIR, filename)

def run_service(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """
    Uruchamia serwis webowy
    
    Args:
        host: Adres hosta
        port: Port
        debug: Tryb debugowania
    """
    logger.info(f"Uruchamianie serwisu na {host}:{port}")
    app.run(host=host, port=port, debug=debug)

# Funkcja do automatycznego generowania dokumentacji API
def generate_api_docs():
    """Generuje dokumentację API na podstawie zarejestrowanych endpointów"""
    docs = {
        "service": SERVICE_INFO["name"],
        "version": SERVICE_INFO["version"],
        "description": SERVICE_INFO["description"],
        "endpoints": []
    }
    
    for endpoint in SERVICE_INFO["endpoints"]:
        endpoint_doc = {
            "path": endpoint["path"],
            "method": endpoint["method"],
            "description": endpoint["description"],
            "parameters": endpoint["params"]
        }
        docs["endpoints"].append(endpoint_doc)
    
    return docs

# Funkcja do ustawienia informacji o serwisie
def set_service_info(name: str, description: str, version: str):
    """
    Ustawia informacje o serwisie
    
    Args:
        name: Nazwa serwisu
        description: Opis serwisu
        version: Wersja serwisu
    """
    SERVICE_INFO["name"] = name
    SERVICE_INFO["description"] = description
    SERVICE_INFO["version"] = version

# Przykład użycia:
if __name__ == "__main__":
    # Ustaw informacje o serwisie
    set_service_info(
        name="Przykładowy Serwis Evopy",
        description="Demonstracja możliwości szablonu serwisu",
        version="1.0.0"
    )
    
    # Przykładowy endpoint API
    @api_endpoint("/api/hello", methods=["GET"], description="Zwraca powitanie")
    def hello(name="Świat"):
        return {"message": f"Witaj, {name}!"}
    
    # Przykładowy endpoint API z metodą POST
    @api_endpoint("/api/echo", methods=["POST"], description="Zwraca przesłane dane")
    def echo(text):
        return {"echo": text}
    
    # Uruchom serwis
    run_service(debug=True)

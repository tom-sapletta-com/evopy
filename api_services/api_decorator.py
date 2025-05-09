#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dekorator do tworzenia usług API w Evopy
"""

import os
import sys
import json
import logging
import functools
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('api_decorator')

class APIService:
    """Klasa do tworzenia usług API w Evopy"""
    
    def __init__(self, name, description, port=5001, host='0.0.0.0'):
        """
        Inicjalizacja usługi API
        
        Args:
            name (str): Nazwa usługi
            description (str): Opis usługi
            port (int): Port, na którym będzie działać usługa
            host (str): Host, na którym będzie działać usługa
        """
        self.name = name
        self.description = description
        self.port = port
        self.host = host
        self.app = Flask(name)
        self.endpoints = []
        self.server_thread = None
        self.running = False
        
        # Dodaj domyślny endpoint dla informacji o usłudze
        @self.app.route('/', methods=['GET'])
        def info():
            return jsonify({
                'name': self.name,
                'description': self.description,
                'endpoints': self.endpoints
            })
    
    def endpoint(self, route, methods=['POST']):
        """
        Dekorator do dodawania endpointów API
        
        Args:
            route (str): Ścieżka endpointu
            methods (list): Lista metod HTTP obsługiwanych przez endpoint
        """
        def decorator(func):
            # Dodaj endpoint do listy endpointów
            self.endpoints.append({
                'route': route,
                'methods': methods,
                'name': func.__name__,
                'description': func.__doc__ or 'Brak opisu'
            })
            
            # Zarejestruj endpoint w aplikacji Flask
            @self.app.route(route, methods=methods)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Pobierz dane z żądania
                    if request.method == 'POST':
                        data = request.json or {}
                    else:
                        data = request.args.to_dict()
                    
                    # Wywołaj funkcję z danymi
                    result = func(data)
                    
                    # Zwróć wynik jako JSON
                    return jsonify(result)
                except Exception as e:
                    logger.error(f"Błąd podczas obsługi żądania: {e}")
                    return jsonify({'error': str(e)}), 500
            
            return wrapper
        
        return decorator
    
    def start(self):
        """Uruchamia usługę API w osobnym wątku"""
        if self.running:
            logger.warning(f"Usługa {self.name} jest już uruchomiona")
            return
        
        def run_server():
            logger.info(f"Uruchamianie usługi {self.name} na {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        
        # Poczekaj na uruchomienie serwera
        time.sleep(1)
        
        logger.info(f"Usługa {self.name} uruchomiona na http://{self.host}:{self.port}")
        return f"http://{self.host}:{self.port}"
    
    def stop(self):
        """Zatrzymuje usługę API"""
        if not self.running:
            logger.warning(f"Usługa {self.name} nie jest uruchomiona")
            return
        
        # Zatrzymaj serwer Flask
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Nie można zatrzymać serwera')
        func()
        
        self.running = False
        logger.info(f"Usługa {self.name} zatrzymana")
    
    def is_running(self):
        """Sprawdza, czy usługa API jest uruchomiona"""
        return self.running

def create_api_service(name, description, port=5001, host='0.0.0.0'):
    """
    Tworzy nową usługę API
    
    Args:
        name (str): Nazwa usługi
        description (str): Opis usługi
        port (int): Port, na którym będzie działać usługa
        host (str): Host, na którym będzie działać usługa
    
    Returns:
        APIService: Nowa usługa API
    """
    return APIService(name, description, port, host)

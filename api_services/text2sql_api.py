#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API dla modułu Text2SQL

Serwis Flask do konwersji tekstu na zapytania SQL.
"""

import os
import sys
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from datetime import datetime

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł Text2SQL i DBManager
from modules.text2sql.text2sql_new import Text2SQL
from modules.base.db_manager import DBManager

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2sql_api')

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Inicjalizacja modułu Text2SQL
text2sql = Text2SQL()

# Inicjalizacja menedżera bazy danych
db_manager = DBManager()

@app.route('/')
def index():
    """Strona główna API"""
    return render_template('module_api.html', 
                          title="Text2SQL API", 
                          module_name="Text2SQL", 
                          description="Konwersja tekstu na zapytania SQL")

@app.route('/api/text2sql', methods=['POST'])
def convert_text_to_sql():
    """Konwertuje tekst na zapytanie SQL"""
    try:
        # Pobierz dane z żądania
        data = request.json
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Brak wymaganego pola "text" w żądaniu'
            }), 400
        
        text = data['text']
        db_schema = data.get('db_schema', '')
        model = data.get('model', text2sql.config['model'])
        temperature = data.get('temperature', text2sql.config['temperature'])
        max_tokens = data.get('max_tokens', text2sql.config['max_tokens'])
        
        # Zapisz zapytanie w bazie danych
        query_id = db_manager.log_query(
            module="text2sql",
            input_text=text,
            parameters={
                'db_schema': db_schema,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        )
        
        # Wykonaj konwersję
        result = text2sql.execute(
            text,
            db_schema=db_schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['result']['code'],
                language="sql",
                success=True
            )
        else:
            db_manager.log_error(
                query_id=query_id,
                error_message=result.get('error', 'Nieznany błąd'),
                error_type="generation_error"
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania żądania: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/text2sql/explain', methods=['POST'])
def explain_sql():
    """Wyjaśnia zapytanie SQL"""
    try:
        # Pobierz dane z żądania
        data = request.json
        if not data or 'sql' not in data:
            return jsonify({
                'success': False,
                'error': 'Brak wymaganego pola "sql" w żądaniu'
            }), 400
        
        sql_code = data['sql']
        
        # Zapisz zapytanie w bazie danych
        query_id = db_manager.log_query(
            module="text2sql_explain",
            input_text=sql_code,
            parameters={}
        )
        
        # Wykonaj wyjaśnienie
        result = text2sql.explain_sql(sql_code)
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['explanation'],
                language="text",
                success=True
            )
        else:
            db_manager.log_error(
                query_id=query_id,
                error_message=result.get('error', 'Nieznany błąd'),
                error_type="explanation_error"
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Błąd podczas wyjaśniania zapytania: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/text2sql/optimize', methods=['POST'])
def optimize_sql():
    """Optymalizuje zapytanie SQL"""
    try:
        # Pobierz dane z żądania
        data = request.json
        if not data or 'sql' not in data:
            return jsonify({
                'success': False,
                'error': 'Brak wymaganego pola "sql" w żądaniu'
            }), 400
        
        sql_code = data['sql']
        
        # Zapisz zapytanie w bazie danych
        query_id = db_manager.log_query(
            module="text2sql_optimize",
            input_text=sql_code,
            parameters={}
        )
        
        # Wykonaj optymalizację
        result = text2sql.optimize_sql(sql_code)
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['optimized_code'],
                language="sql",
                success=True
            )
        else:
            db_manager.log_error(
                query_id=query_id,
                error_message=result.get('error', 'Nieznany błąd'),
                error_type="optimization_error"
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Błąd podczas optymalizacji zapytania: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Uruchomienie aplikacji
if __name__ == '__main__':
    # Utwórz katalog dla zapytań SQL, jeśli nie istnieje
    if text2sql.sql_dir:
        os.makedirs(text2sql.sql_dir, exist_ok=True)
    
    # Uruchom aplikację Flask
    app.run(host='0.0.0.0', port=5002, debug=True)

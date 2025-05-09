#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API dla modułu SQL2Text

Serwis Flask do konwersji zapytań SQL na opisy w języku naturalnym.
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

# Importuj moduł SQL2Text i DBManager
from modules.sql2text.sql2text_new import SQL2Text
from modules.base.db_manager import DBManager

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('sql2text_api')

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Inicjalizacja modułu SQL2Text
sql2text = SQL2Text()

# Inicjalizacja menedżera bazy danych
db_manager = DBManager()

@app.route('/')
def index():
    """Strona główna API"""
    return render_template('module_api.html', 
                          title="SQL2Text API", 
                          module_name="SQL2Text", 
                          description="Konwersja zapytań SQL na opisy w języku naturalnym")

@app.route('/api/sql2text', methods=['POST'])
def convert_sql_to_text():
    """Konwertuje zapytanie SQL na opis w języku naturalnym"""
    try:
        # Pobierz dane z żądania
        data = request.json
        if not data or 'sql' not in data:
            return jsonify({
                'success': False,
                'error': 'Brak wymaganego pola "sql" w żądaniu'
            }), 400
        
        sql_code = data['sql']
        detail_level = data.get('detail_level', 'standard')  # standard, basic, detailed
        model = data.get('model', sql2text.config['model'])
        temperature = data.get('temperature', sql2text.config['temperature'])
        max_tokens = data.get('max_tokens', sql2text.config['max_tokens'])
        
        # Zapisz zapytanie w bazie danych
        query_id = db_manager.log_query(
            module="sql2text",
            input_text=sql_code,
            parameters={
                'detail_level': detail_level,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        )
        
        # Wykonaj konwersję
        result = sql2text.execute(
            sql_code,
            detail_level=detail_level,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['result']['description'],
                language="text",
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

@app.route('/api/sql2text/analyze', methods=['POST'])
def analyze_sql():
    """Analizuje zapytanie SQL i zwraca jego strukturę i potencjalne problemy"""
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
            module="sql2text_analyze",
            input_text=sql_code,
            parameters={}
        )
        
        # Wykonaj analizę
        result = sql2text.analyze_sql_query(sql_code)
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['analysis'],
                language="text",
                success=True
            )
        else:
            db_manager.log_error(
                query_id=query_id,
                error_message=result.get('error', 'Nieznany błąd'),
                error_type="analysis_error"
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Błąd podczas analizy zapytania: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sql2text/example-data', methods=['POST'])
def generate_example_data():
    """Generuje przykładowe dane, które pasują do zapytania SQL"""
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
            module="sql2text_example_data",
            input_text=sql_code,
            parameters={}
        )
        
        # Wykonaj generowanie przykładowych danych
        result = sql2text.generate_example_data(sql_code)
        
        # Zapisz wynik w bazie danych
        if result['success']:
            db_manager.log_code_generation(
                query_id=query_id,
                generated_code=result['example_data'],
                language="sql",
                success=True
            )
        else:
            db_manager.log_error(
                query_id=query_id,
                error_message=result.get('error', 'Nieznany błąd'),
                error_type="example_data_error"
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Błąd podczas generowania przykładowych danych: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Uruchomienie aplikacji
if __name__ == '__main__':
    # Utwórz katalog wyjściowy, jeśli nie istnieje
    if sql2text.output_dir:
        os.makedirs(sql2text.output_dir, exist_ok=True)
    
    # Uruchom aplikację Flask
    app.run(host='0.0.0.0', port=5003, debug=True)

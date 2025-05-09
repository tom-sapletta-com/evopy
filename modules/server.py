#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import logging
import datetime
import importlib.util
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Konfiguracja logowania
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(MODULES_DIR)
LOG_DIR = os.path.join(MODULES_DIR, 'logs')
HISTORY_DIR = os.path.join(APP_DIR, 'history')

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

logger = logging.getLogger('modules-server')

app = Flask(__name__)

# Lista modułów konwersji
CONVERTERS = [
    {"name": "text2python", "description": "Konwersja tekstu na kod Python"},
    {"name": "python2text", "description": "Konwersja kodu Python na opis tekstowy"},
    {"name": "text2shell", "description": "Konwersja tekstu na polecenia shell"},
    {"name": "shell2text", "description": "Konwersja poleceń shell na opis tekstowy"},
    {"name": "text2sql", "description": "Konwersja tekstu na zapytania SQL"},
    {"name": "sql2text", "description": "Konwersja zapytań SQL na opis tekstowy"},
    {"name": "text2regex", "description": "Konwersja tekstu na wyrażenia regularne"},
    {"name": "regex2text", "description": "Konwersja wyrażeń regularnych na opis tekstowy"}
]

def module_exists(module_name):
    """Sprawdza, czy moduł istnieje w nowej strukturze katalogów"""
    module_dir = os.path.join(MODULES_DIR, module_name)
    module_file = os.path.join(module_dir, f"{module_name}.py")
    return os.path.exists(module_file)

def get_module_content(module_name):
    """Pobiera zawartość pliku modułu"""
    module_file = os.path.join(MODULES_DIR, module_name, f"{module_name}.py")
    if os.path.exists(module_file):
        with open(module_file, 'r') as f:
            return f.read()
    return None

@app.route('/')
def index():
    """Strona główna z listą modułów konwersji"""
    logger.info("Dostęp do strony głównej")
    
    # Sprawdź, które moduły faktycznie istnieją
    available_converters = []
    for converter in CONVERTERS:
        if module_exists(converter["name"]):
            available_converters.append(converter)
    
    return render_template('index.html', converters=available_converters)

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
    
    if not module_exists(name):
        return "Moduł nie istnieje", 404
    
    content = get_module_content(name)
    if content is None:
        return "Nie można odczytać zawartości modułu", 500
    
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

@app.route('/api/convert', methods=['POST'])
def convert():
    """API do konwersji tekstu przy użyciu wybranego modułu"""
    data = request.json
    if not data:
        return jsonify({"error": "Brak danych wejściowych"}), 400
    
    module_name = data.get('module')
    input_text = data.get('input')
    
    if not module_name or not input_text:
        return jsonify({"error": "Brak wymaganego parametru: module lub input"}), 400
    
    logger.info(f"Żądanie konwersji przy użyciu modułu: {module_name}")
    
    if not module_exists(module_name):
        return jsonify({"error": f"Moduł {module_name} nie istnieje"}), 404
    
    try:
        # Dynamiczne importowanie modułu
        module_path = os.path.join(MODULES_DIR, module_name, f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Zakładamy, że każdy moduł ma klasę o tej samej nazwie co moduł
        # np. text2python.py ma klasę Text2Python
        class_name = ''.join(word.capitalize() for word in module_name.split('2'))
        converter_class = getattr(module, class_name)
        
        # Inicjalizacja konwertera
        converter = converter_class()
        
        # Konwersja tekstu
        result = converter.convert(input_text)
        
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"Błąd podczas konwersji: {str(e)}")
        return jsonify({"error": f"Błąd podczas konwersji: {str(e)}"}), 500

@app.route('/conversations')
def list_conversations():
    """Wyświetla listę konwersacji"""
    logger.info("Dostęp do listy konwersacji")
    try:
        conversations = []
        history_dir = Path(HISTORY_DIR)
        
        if not os.path.exists(history_dir):
            return render_template('conversations.html', error="Katalog historii konwersacji nie istnieje", conversations=[])
        
        # Pobierz wszystkie pliki JSON z katalogu historii
        for file in history_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                    
                    # Przygotuj dane do wyświetlenia
                    conversation_data = {
                        "id": conversation.get("id", file.stem),
                        "title": conversation.get("title", "Bez tytułu"),
                        "created_at": conversation.get("created_at", ""),
                        "updated_at": conversation.get("updated_at", ""),
                        "message_count": len(conversation.get("messages", []))
                    }
                    
                    # Formatuj daty
                    for date_field in ["created_at", "updated_at"]:
                        if conversation_data[date_field]:
                            try:
                                dt = datetime.fromisoformat(conversation_data[date_field])
                                conversation_data[date_field] = dt.strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                pass
                    
                    conversations.append(conversation_data)
            except Exception as e:
                logger.error(f"Błąd podczas odczytu pliku konwersacji {file}: {str(e)}")
        
        # Sortuj konwersacje według daty aktualizacji (najnowsze pierwsze)
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return render_template('conversations.html', conversations=conversations)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania listy konwersacji: {str(e)}")
        return render_template('conversations.html', error=f"Wystąpił błąd: {str(e)}", conversations=[])

@app.route('/conversation/<string:conversation_id>')
def conversation_details(conversation_id):
    """Wyświetla szczegóły konwersacji"""
    logger.info(f"Dostęp do szczegółów konwersacji: {conversation_id}")
    try:
        conversation_file = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
        
        if not os.path.exists(conversation_file):
            return render_template('conversations.html', error=f"Konwersacja o ID {conversation_id} nie istnieje", conversations=[])
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        # Przygotuj dane do wyświetlenia
        conversation_data = {
            "id": conversation.get("id", conversation_id),
            "title": conversation.get("title", "Bez tytułu"),
            "created_at": conversation.get("created_at", ""),
            "updated_at": conversation.get("updated_at", ""),
            "message_count": len(conversation.get("messages", [])),
            "messages": [],
            "code_executions": conversation.get("code_executions", [])
        }
        
        # Formatuj daty
        for date_field in ["created_at", "updated_at"]:
            if conversation_data[date_field]:
                try:
                    dt = datetime.fromisoformat(conversation_data[date_field])
                    conversation_data[date_field] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
        
        # Przygotuj wiadomości
        for message in conversation.get("messages", []):
            message_data = {
                "role": message.get("role", "system"),
                "content": message.get("content", ""),
                "timestamp": ""
            }
            
            # Formatuj datę wiadomości
            if "timestamp" in message:
                try:
                    dt = datetime.fromisoformat(message["timestamp"])
                    message_data["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            
            # Formatuj treść wiadomości (zamień kod na znaczniki <pre><code>)
            content = message_data["content"]
            # Zamień bloki kodu oznaczone ```
            if "```" in content:
                parts = content.split("```")
                formatted_content = parts[0]
                
                for i in range(1, len(parts), 2):
                    if i < len(parts):
                        code_block = parts[i].strip()
                        formatted_content += f"<pre><code>{code_block}</code></pre>"
                        if i + 1 < len(parts):
                            formatted_content += parts[i+1]
                
                message_data["content"] = formatted_content
            
            conversation_data["messages"].append(message_data)
        
        return render_template('conversation_details.html', conversation=conversation_data)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania szczegółów konwersacji: {str(e)}")
        return render_template('conversations.html', error=f"Wystąpił błąd: {str(e)}", conversations=[])

if __name__ == '__main__':
    # Utwórz katalog templates, jeśli nie istnieje
    templates_dir = os.path.join(MODULES_DIR, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Sprawdź, czy katalog templates istnieje w converters i skopiuj szablony, jeśli to konieczne
    old_templates_dir = os.path.join(MODULES_DIR, 'converters', 'templates')
    if os.path.exists(old_templates_dir) and not os.listdir(templates_dir):
        logger.info("Kopiowanie szablonów z katalogu converters")
        for template_file in os.listdir(old_templates_dir):
            src_file = os.path.join(old_templates_dir, template_file)
            dst_file = os.path.join(templates_dir, template_file)
            if os.path.isfile(src_file) and not os.path.exists(dst_file):
                with open(src_file, 'r') as src, open(dst_file, 'w') as dst:
                    dst.write(src.read())
    
    app.run(debug=True, host='0.0.0.0', port=5000)

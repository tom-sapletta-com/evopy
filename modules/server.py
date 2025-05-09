#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import logging
import importlib.util
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory

# Import custom filters
from custom_filters import register_filters

# Konfiguracja logowania
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(MODULES_DIR)
LOG_DIR = os.path.join(MODULES_DIR, 'logs')
HISTORY_DIR = os.path.join(APP_DIR, 'history')

os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f'server_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

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

# Register custom filters
register_filters(app)

# Configure static folder for images
app.config['UPLOAD_FOLDER'] = os.path.join(APP_DIR, 'output', 'images')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Lista modułów konwersji
CONVERTERS = [
    {"name": "text2python", "description": "Konwersja tekstu na kod Python"},
    {"name": "python2text", "description": "Konwersja kodu Python na opis tekstowy"},
    {"name": "text2shell", "description": "Konwersja tekstu na polecenia shell"},
    {"name": "shell2text", "description": "Konwersja poleceń shell na opis tekstowy"},
    {"name": "text2sql", "description": "Konwersja tekstu na zapytania SQL"},
    {"name": "sql2text", "description": "Konwersja zapytań SQL na opis tekstowy"},
    {"name": "text2regex", "description": "Konwersja tekstu na wyrażenia regularne"},
    {"name": "regex2text", "description": "Konwersja wyrażeń regularnych na opis tekstowy"},
    {"name": "text2docker", "description": "Konwersja tekstu na polecenia Docker"},
    {"name": "docker2text", "description": "Konwersja poleceń Docker na opis tekstowy"},
    {"name": "text2python_docker", "description": "Konwersja tekstu na kod Python i uruchomienie w Dockerze"},
    {"name": "text2speech", "description": "Konwersja tekstu na mowę (text-to-speech)"},
    {"name": "text2email", "description": "Konwersja tekstu na wiadomości email"},
    {"name": "text2notification", "description": "Konwersja tekstu na powiadomienia systemowe"},
    {"name": "text2image", "description": "Konwersja tekstu na obrazy i diagramy"},
    {"name": "text2discord", "description": "Konwersja tekstu na wiadomości Discord"},
    {"name": "text2telegram", "description": "Konwersja tekstu na wiadomości Telegram"}
]

# Importuj moduł do przechowywania zadań Docker
from docker_tasks_store import DOCKER_TASKS, docker_tasks, web_services, get_all_docker_tasks, get_all_web_services
from docker_tasks_store import register_docker_container as store_register_docker_container
from docker_tasks_store import get_docker_task as store_get_docker_task

# Słownik do przechowywania aktywnych kontenerów Docker
docker_containers = {}

# Zapisz te słowniki w zmiennych aplikacji Flask, aby były dostępne w całej aplikacji
def init_app_variables(app):
    app.config['DOCKER_TASKS'] = DOCKER_TASKS
    app.config['docker_containers'] = docker_containers
    app.config['web_services'] = web_services
    
    # Dodaj funkcję pomocniczą do szablonu Jinja2
    @app.template_global()
    def get_docker_task(task_id):
        return store_get_docker_task(task_id)

# Funkcja do rejestrowania kontenera Docker dla zadania
def register_docker_container(task_id, container_id, code, output, is_service=False, service_url=None, service_name=None):
    """Rejestruje kontener Docker dla zadania"""
    # Użyj funkcji z modułu docker_tasks_store
    task_info = store_register_docker_container(task_id, container_id, code, output, is_service, service_url, service_name)
    logger.info(f"Zarejestrowano kontener {container_id} dla zadania {task_id}")
    return task_info

def module_exists(module_name):
    """Sprawdza, czy moduł istnieje w nowej strukturze katalogów"""
    module_dir = os.path.join(MODULES_DIR, module_name)
    # Sprawdź, czy istnieje plik modułu lub katalog z __init__.py
    module_file = os.path.join(module_dir, f"{module_name}.py")
    init_file = os.path.join(module_dir, "__init__.py")
    return os.path.exists(module_file) or os.path.exists(init_file)

def get_module_content(module_name):
    """Pobiera zawartość pliku modułu"""
    module_file = os.path.join(MODULES_DIR, module_name, f"{module_name}.py")
    init_file = os.path.join(MODULES_DIR, module_name, "__init__.py")
    
    if os.path.exists(module_file):
        with open(module_file, 'r') as f:
            return f.read()
    elif os.path.exists(init_file):
        with open(init_file, 'r') as f:
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
        # Upewnij się, że mamy najnowsze zadania Docker
        from docker_tasks_store import load_tasks, DOCKER_TASKS, web_services
        load_tasks()  # Załaduj najnowsze zadania z pliku
        
        logger.info(f"Załadowano {len(DOCKER_TASKS)} zadań Docker")
        
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
                    container_id = parts[0]
                    # Sprawdź, czy kontener jest powiązany z zadaniem
                    task_id = None
                    is_service = False
                    service_url = None
                    service_name = None
                    
                    for tid, info in DOCKER_TASKS.items():
                        if info.get('container_id') == container_id:
                            task_id = tid
                            is_service = info.get('is_service', False)
                            service_url = info.get('service_url')
                            service_name = info.get('service_name')
                            break
                    
                    containers.append({
                        "id": container_id,
                        "image": parts[1],
                        "status": parts[2],
                        "name": parts[3],
                        "task_id": task_id,
                        "is_service": is_service,
                        "service_url": service_url,
                        "service_name": service_name
                    })
        
        # Dodaj informacje o zadaniach Docker do kontekstu szablonu
        all_docker_tasks = dict(DOCKER_TASKS)  # Skopiuj słownik, aby uniknąć problemów z referencjami
        
        logger.info(f"Przekazywanie {len(all_docker_tasks)} zadań Docker do szablonu")
        
        return render_template('docker.html', 
                               containers=containers, 
                               docker_tasks=all_docker_tasks, 
                               web_services=web_services)
    except subprocess.CalledProcessError as e:
        error_message = f"Błąd podczas pobierania listy kontenerów Docker: {e.stderr}"
        return render_template('docker.html', error=error_message, containers=[], docker_tasks={})
    except Exception as e:
        error_message = f"Wystąpił nieoczekiwany błąd: {str(e)}"
        logger.error(f"Błąd w docker_containers: {e}", exc_info=True)
        return render_template('docker.html', error=error_message, containers=[], docker_tasks={})

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

@app.route('/docker/register', methods=['POST'])
def register_docker_task():
    """Rejestruje zadanie Docker bezpośrednio"""
    task_id = request.form.get('task_id', str(uuid.uuid4()))
    container_id = request.form.get('container_id', '')
    code = request.form.get('code', '')
    output = request.form.get('output', '')
    is_service = request.form.get('is_service', 'false').lower() == 'true'
    service_url = request.form.get('service_url', None)
    service_name = request.form.get('service_name', None)
    user_prompt = request.form.get('user_prompt', None)
    agent_explanation = request.form.get('agent_explanation', None)
    
    logger.info(f"Rejestrowanie zadania Docker: {task_id} dla kontenera {container_id}")
    
    if not container_id:
        return jsonify({"error": "Brak identyfikatora kontenera"}), 400
    
    try:
        # Zarejestruj kontener Docker dla zadania
        task_info = {
            "container_id": container_id,
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "output": output,
            "is_service": is_service,
            "service_url": service_url,
            "service_name": service_name,
            "user_prompt": user_prompt,
            "agent_explanation": agent_explanation
        }
        
        # Zapisz zadanie w słowniku
        DOCKER_TASKS[task_id] = task_info
        
        # Jeśli to serwis webowy, dodaj go również do słownika serwisów
        if is_service and service_url:
            web_services[task_id] = {
                "container_id": container_id,
                "timestamp": datetime.now().isoformat(),
                "service_url": service_url,
                "service_name": service_name or f"Service {task_id[:8]}"
            }
        
        # Zapisz zadania do pliku
        from docker_tasks_store import save_tasks
        save_tasks()
        
        logger.info(f"Zarejestrowano zadanie Docker: {task_id}")
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "container_id": container_id,
            "docker_url": f"http://localhost:5000/docker/{task_id}"
        })
    except Exception as e:
        logger.error(f"Błąd podczas rejestrowania zadania Docker: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/docker/run', methods=['POST'])
def docker_run():
    """Uruchamia polecenie Docker"""
    command = request.form.get('command', '')
    task_id = request.form.get('task_id', str(uuid.uuid4()))
    is_service = request.form.get('is_service', 'false').lower() == 'true'
    service_url = request.form.get('service_url', None)
    service_name = request.form.get('service_name', None)
    
    logger.info(f"Uruchamianie polecenia Docker: {command} dla zadania {task_id}")
    
    if not command:
        return jsonify({"error": "Brak polecenia"}), 400
    
    try:
        # Uruchom polecenie Docker
        result = subprocess.run(
            ["docker"] + command.split(),
            capture_output=True,
            text=True
        )
        
        # Jeśli to polecenie tworzy kontener, zarejestruj go
        if command.startswith('run') and result.returncode == 0:
            container_id = result.stdout.strip()
            register_docker_container(task_id, container_id, command, result.stdout, is_service, service_url, service_name)
            
            return jsonify({
                "success": True,
                "container_id": container_id,
                "output": result.stdout,
                "is_service": is_service,
                "service_url": service_url
            })
        else:
            return jsonify({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "task_id": task_id,
                "docker_url": f"http://localhost:5000/docker/{task_id}"
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

@app.route('/docker/<string:task_id>')
def docker_task_details(task_id):
    """Szczegóły zadania Docker"""
    logger.info(f"Dostęp do szczegółów zadania Docker: {task_id}")
    
    # Pobierz informacje o zadaniu
    task_info = DOCKER_TASKS.get(task_id)
    if not task_info:
        return "Zadanie nie istnieje", 404
    
    # Sprawdzamy format zadania i dostosowujemy go do nowego formatu, jeśli potrzeba
    if 'status' not in task_info:
        # Pobierz status kontenera
        container_id = task_info.get('container_id')
        container_exists = False
        container_status = "Nieznany"
        
        if container_id:
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    container_exists = True
                    container_status = result.stdout.strip()
                    task_info['status'] = container_status
                else:
                    task_info['status'] = "Kontener nie jest aktywny"
            except Exception as e:
                logger.error(f"Błąd podczas sprawdzania statusu kontenera: {e}")
                task_info['status'] = f"Błąd: {str(e)}"
        
        # Dodajemy informacje o kontenerze do kontekstu szablonu dla kompatybilności wstecznej
        return render_template(
            'docker_task.html', 
            task_id=task_id, 
            task_info=task_info, 
            container_exists=container_exists,
            container_status=container_status
        )
    else:
        # Nowy format zadania, sprawdzamy czy to serwis
        container_id = task_info.get('container_id')
        if container_id:
            try:
                # Sprawdzamy aktualny status kontenera
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )
                status = result.stdout.strip() or "Kontener nie jest aktywny"
                task_info['status'] = status
                
                # Jeśli to serwis, pobierz dodatkowe informacje
                if task_info.get('is_service'):
                    # Pobierz logi kontenera
                    try:
                        logs_result = subprocess.run(
                            ["docker", "logs", "--tail", "50", container_id],
                            capture_output=True,
                            text=True
                        )
                        task_info['logs'] = logs_result.stdout
                    except Exception as e:
                        task_info['logs'] = f"Błąd podczas pobierania logów: {str(e)}"
            except Exception as e:
                task_info['status'] = f"Błąd podczas pobierania statusu: {str(e)}"
        
        return render_template('docker_task.html', task_id=task_id, task_info=task_info)

@app.route('/api/docker_task/<string:task_id>')
def api_docker_task(task_id):
    """API do pobierania informacji o zadaniu Docker"""
    if task_id not in docker_tasks:
        return jsonify({"error": "Zadanie nie istnieje"}), 404
    
    return jsonify(docker_tasks[task_id])
@app.route('/static/images/<path:filename>')
def serve_image(filename):
    """Serwuje pliki obrazów"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/services')
def list_services():
    """Strona z listą serwisów webowych"""
    logger.info("Dostęp do strony z serwisami webowymi")
    
    # Sprawdź status każdego serwisu
    active_services = {}
    for task_id, service_info in web_services.items():
        container_id = service_info.get('container_id')
        if container_id:
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                status = result.stdout.strip() or "Nieaktywny"
                service_info['status'] = status
                
                # Jeśli kontener jest aktywny, dodaj go do listy aktywnych serwisów
                if status != "Nieaktywny":
                    active_services[task_id] = service_info
            except Exception as e:
                service_info['status'] = f"Błąd: {str(e)}"
    
    return render_template('services.html', services=active_services)

@app.route('/service/<string:task_id>')
def service_details(task_id):
    """Szczegóły serwisu webowego"""
    logger.info(f"Dostęp do szczegółów serwisu: {task_id}")
    
    # Pobierz informacje o serwisie
    service_info = web_services.get(task_id)
    if not service_info:
        return "Serwis nie istnieje", 404
    
    # Pobierz szczegółowe informacje o kontenerze
    container_id = service_info.get('container_id')
    if container_id:
        try:
            # Status kontenera
            status_result = subprocess.run(
                ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                check=True
            )
            service_info['status'] = status_result.stdout.strip() or "Nieaktywny"
            
            # Logi kontenera
            logs_result = subprocess.run(
                ["docker", "logs", "--tail", "50", container_id],
                capture_output=True,
                text=True
            )
            service_info['logs'] = logs_result.stdout
            
            # Pobierz informacje o portach
            ports_result = subprocess.run(
                ["docker", "port", container_id],
                capture_output=True,
                text=True
            )
            service_info['ports'] = ports_result.stdout
        except Exception as e:
            service_info['error'] = str(e)
    
    # Pobierz informacje o zadaniu Docker
    task_info = docker_tasks.get(task_id, {})
    
    return render_template('service_details.html', task_id=task_id, service_info=service_info, task_info=task_info)

@app.route('/service/stop/<string:task_id>', methods=['POST'])
def stop_service(task_id):
    """Zatrzymuje serwis webowy"""
    logger.info(f"Zatrzymywanie serwisu: {task_id}")
    
    # Pobierz informacje o serwisie
    service_info = web_services.get(task_id)
    if not service_info:
        return jsonify({"error": "Serwis nie istnieje"}), 404
    
    # Zatrzymaj kontener
    container_id = service_info.get('container_id')
    if container_id:
        try:
            subprocess.run(
                ["docker", "stop", container_id],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"success": True, "message": "Serwis został zatrzymany"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Brak identyfikatora kontenera"}), 400

@app.route('/service/restart/<string:task_id>', methods=['POST'])
def restart_service(task_id):
    """Restartuje serwis webowy"""
    logger.info(f"Restartowanie serwisu: {task_id}")
    
    # Pobierz informacje o serwisie
    service_info = web_services.get(task_id)
    if not service_info:
        return jsonify({"error": "Serwis nie istnieje"}), 404
    
    # Restartuj kontener
    container_id = service_info.get('container_id')
    if container_id:
        try:
            subprocess.run(
                ["docker", "restart", container_id],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"success": True, "message": "Serwis został zrestartowany"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Brak identyfikatora kontenera"}), 400

# Inicjalizuj zmienne aplikacji
init_app_variables(app)

# Utwórz katalogi potrzebne do działania aplikacji
templates_dir = os.path.join(MODULES_DIR, 'templates')
os.makedirs(templates_dir, exist_ok=True)

static_dir = os.path.join(MODULES_DIR, 'static')
os.makedirs(static_dir, exist_ok=True)

# Utwórz katalogi dla nowych modułów
for module_name in [m['name'] for m in CONVERTERS]:
    module_dir = os.path.join(MODULES_DIR, module_name)
    os.makedirs(module_dir, exist_ok=True)

if __name__ == '__main__':
    # Uruchom serwer Flask
    app.run(host='0.0.0.0', port=5000, debug=True)

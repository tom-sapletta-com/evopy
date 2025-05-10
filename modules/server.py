#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import logging
import importlib.util
import uuid
import traceback
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory

# Import custom filters
from custom_filters import register_filters

# Konfiguracja logowania
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULES_DIR)

# Konfiguracja katalogów logów
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'server.log')

# Ścieżka do katalogu z konwersacjami (w katalogu domowym użytkownika)
HOME_DIR = os.path.expanduser('~')
EVO_APP_DIR = os.path.join(HOME_DIR, '.evo-assistant')
HISTORY_DIR = os.path.join(EVO_APP_DIR, 'history')

# Konfiguracja logowania do pliku i konsoli
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Utworzenie loggera
logger = logging.getLogger('evopy-server')

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
        from docker_tasks_store import load_tasks, DOCKER_TASKS, web_services, save_tasks
        
        # Wymuś załadowanie najnowszych danych z pliku
        load_tasks()  # Załaduj najnowsze zadania z pliku
        
        # Sprawdź aktualny stan kontenerów i zaktualizuj status
        try:
            # Pobierz listę wszystkich kontenerów (również zatrzymanych)
            all_containers = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.ID}}\t{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Utwórz listę ID kontenerów i słownik nazwa->ID
            container_ids_list = []
            container_names_dict = {}
            
            for line in all_containers.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        container_id = parts[0]
                        container_name = parts[1]
                        container_ids_list.append(container_id)
                        container_names_dict[container_name] = container_id
            
            logger.info(f"Znaleziono {len(container_ids_list)} aktywnych kontenerów Docker")
            
            # Zaktualizuj status kontenerów w DOCKER_TASKS
            for task_id, task_info in DOCKER_TASKS.items():
                container_id = task_info.get('container_id')
                
                # Sprawdź czy kontener istnieje - albo po ID, albo po nazwie
                if container_id in container_ids_list or container_id in container_names_dict:
                    # Kontener istnieje, zaktualizuj status
                    task_info['container_exists'] = True
                else:
                    # Kontener nie istnieje
                    task_info['container_exists'] = False
            
            # Zapisz zaktualizowane dane
            save_tasks()
            
        except Exception as e:
            logger.warning(f"Błąd podczas aktualizacji statusów kontenerów: {e}")
        
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
        # Sprawdź, czy kontener istnieje
        container_exists = True
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.ID}}"],
                capture_output=True,
                text=True
            )
            if not result.stdout.strip():
                container_exists = False
                logger.warning(f"Kontener {container_id} nie istnieje, ale zadanie zostanie zarejestrowane")
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania istnienia kontenera: {e}")
        
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
            "agent_explanation": agent_explanation,
            "container_exists": container_exists
        }
        
        # Zapisz zadanie w słowniku
        DOCKER_TASKS[task_id] = task_info
        
        # Jeśli to serwis webowy, dodaj go również do słownika serwisów niezależnie od tego, czy kontener istnieje
        if is_service:
            service_info = {
                "container_id": container_id,
                "timestamp": datetime.now().isoformat(),
                "container_exists": container_exists
            }
            
            if service_url:
                service_info["service_url"] = service_url
                logger.info(f"Zarejestrowano URL serwisu: {service_url} dla zadania {task_id}")
            
            if service_name:
                service_info["service_name"] = service_name
            else:
                service_info["service_name"] = f"Serwis {task_id[:8]}"
                
            web_services[task_id] = service_info
        
        # Zapisz zadania do pliku
        try:
            from docker_tasks_store import save_tasks, register_docker_container
            
            # Użyj funkcji z modułu do rejestracji zadania
            register_docker_container(
                task_id=task_id,
                container_id=container_id,
                code=code,
                output=output,
                is_service=is_service,
                service_url=service_url,
                service_name=service_name,
                user_prompt=user_prompt,
                agent_explanation=agent_explanation,
                container_exists=container_exists
            )
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania zadań Docker: {e}")
            # Spróbuj bezpośrednio zapisać zadania
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
    logger.info(f"Dostęp do listy konwersacji z katalogu: {HISTORY_DIR}")
    try:
        conversations = []
        history_dir = Path(HISTORY_DIR)
        
        if not os.path.exists(history_dir):
            logger.warning(f"Katalog historii konwersacji nie istnieje: {history_dir}")
            return render_template('conversations.html', 
                                  error=f"Katalog historii konwersacji nie istnieje: {history_dir}", 
                                  conversations=[])
        
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
        # Pobierz konwersację z pliku
        conversation_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
        logger.info(f"Próba odczytu konwersacji z: {conversation_path}")
        
        if not os.path.exists(conversation_path):
            logger.warning(f"Konwersacja o ID {conversation_id} nie istnieje w ścieżce: {conversation_path}")
            return render_template('conversations.html', error=f"Konwersacja o ID {conversation_id} nie istnieje", conversations=[])
        
        with open(conversation_path, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        # Przygotuj dane do wyświetlenia
        conversation_data = {
            "id": conversation.get("id", conversation_id),
            "title": conversation.get("title", "Bez tytułu"),
            "created_at": conversation.get("created_at", ""),
            "updated_at": conversation.get("updated_at", ""),
            "message_count": len(conversation.get("messages", [])),
            "messages": [],
            "code_executions": conversation.get("code_executions", []),
            "docker_tasks": []
        }
        
        # Znajdź powiązane zadania Docker
        for execution in conversation_data["code_executions"]:
            if "docker_task_id" in execution:
                conversation_data["docker_tasks"].append(execution["docker_task_id"])
            
        # Szukaj również linków do Docker w treści wiadomości
        for message in conversation.get("messages", []):
            content = message.get("content", "")
            if "http://localhost:5000/docker/" in content:
                # Wyodrębnij ID zadania Docker z linku
                import re
                docker_links = re.findall(r'http://localhost:5000/docker/([\w-]+)', content)
                for task_id in docker_links:
                    if task_id not in conversation_data["docker_tasks"]:
                        conversation_data["docker_tasks"].append(task_id)
        
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

@app.route('/docker/<string:task_id>/continue', methods=['POST'])
def docker_task_continue(task_id):
    """Kontynuacja konwersacji dla zadania Docker"""
    logger.info(f"Kontynuacja konwersacji dla zadania Docker: {task_id}")
    
    # Pobierz prompt z formularza
    prompt = request.form.get('prompt')
    use_sandbox = request.form.get('use_sandbox') == 'true'
    
    if not prompt:
        flash("Prompt nie może być pusty", "danger")
        return redirect(url_for('docker_task_details', task_id=task_id))
    
    # Pobierz informacje o zadaniu Docker
    try:
        from docker_tasks_store import load_tasks, get_docker_task
        load_tasks()
        task_info = get_docker_task(task_id)
    except Exception as e:
        logger.error(f"Błąd podczas ładowania zadań Docker: {e}")
        task_info = DOCKER_TASKS.get(task_id)
    
    if not task_info:
        flash("Zadanie nie istnieje", "danger")
        return redirect(url_for('docker_containers'))
    
    # Pobierz kod z zadania
    code = task_info.get('code', '')
    
    # Dynamicznie importuj moduł text2python
    try:
        # Pobierz ścieżkę do modułu text2python
        module_path = os.path.join(MODULES_DIR, 'text2python', 'text2python.py')
        
        # Sprawdź, czy plik istnieje
        if not os.path.exists(module_path):
            logger.error(f"Nie znaleziono modułu text2python pod ścieżką: {module_path}")
            flash("Nie znaleziono modułu text2python", "danger")
            return redirect(url_for('docker_task_details', task_id=task_id))
        
        # Dynamicznie importuj moduł
        spec = importlib.util.spec_from_file_location('text2python', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Inicjalizacja konwertera
        converter = module.Text2Python()
        logger.info(f"Pomyślnie zainicjalizowano konwerter Text2Python dla promptu: {prompt}")
        
        # Generowanie kodu na podstawie promptu
        logger.info(f"Generowanie kodu dla promptu: {prompt}")
        result = converter.process(prompt)
        
        if not result.get("success", False):
            error_msg = result.get('error', 'Nieznany błąd')
            logger.error(f"Błąd podczas generowania kodu: {error_msg}")
            flash(f"Błąd podczas generowania kodu: {error_msg}", "danger")
            return redirect(url_for('docker_task_details', task_id=task_id))
        
        # Pobierz wygenerowany kod
        new_code = result.get("code", "")
        logger.info(f"Wygenerowano kod: {new_code[:100]}...")
        
        # Wykonaj kod w piaskownicy Docker
        logger.info(f"Wykonywanie kodu w piaskownicy Docker (use_sandbox={use_sandbox})")
        execution_result = converter.execute_code(new_code, use_sandbox=use_sandbox)
        
        # Sprawdź, czy wykonanie zakończyło się sukcesem
        if not execution_result.get("success", False):
            error_msg = execution_result.get('error', 'Nieznany błąd podczas wykonania kodu')
            logger.error(f"Błąd podczas wykonania kodu: {error_msg}")
            flash(f"Błąd podczas wykonania kodu: {error_msg}", "danger")
            
            # Mimo błędu, zarejestruj zadanie Docker, aby zachować informacje o błędzie
            new_task_id = str(uuid.uuid4())
            container_id = execution_result.get("container_name", f"evopy-sandbox-{new_task_id}")
            
            from docker_tasks_store import register_docker_container
            register_docker_container(
                task_id=new_task_id,
                container_id=container_id,
                code=new_code,
                output=execution_result,
                is_service=False,
                user_prompt=prompt,
                container_exists=False
            )
            
            return redirect(url_for('docker_task_details', task_id=new_task_id))
        
        # Utwórz nowe zadanie Docker
        new_task_id = str(uuid.uuid4())
        container_id = execution_result.get("container_name", f"evopy-sandbox-{new_task_id}")
        logger.info(f"Utworzono nowe zadanie Docker: {new_task_id} dla kontenera: {container_id}")
        
        # Zarejestruj nowe zadanie Docker
        from docker_tasks_store import register_docker_container
        task_info = register_docker_container(
            task_id=new_task_id,
            container_id=container_id,
            code=new_code,
            output=execution_result,
            is_service=False,
            user_prompt=prompt,
            container_exists=True
        )
        
        logger.info(f"Zarejestrowano zadanie Docker: {new_task_id}")
        flash(f"Pomyślnie wygenerowano i wykonano kod dla promptu: {prompt}", "success")
        
        # Przekieruj do nowego zadania Docker
        return redirect(url_for('docker_task_details', task_id=new_task_id))
    
    except Exception as e:
        logger.error(f"Błąd podczas kontynuacji konwersacji: {e}")
        flash(f"Błąd podczas kontynuacji konwersacji: {e}", "danger")
        return redirect(url_for('docker_task_details', task_id=task_id))

@app.route('/docker/<string:task_id>')
def docker_task_details(task_id):
    """Szczegóły zadania Docker"""
    logger.info(f"Dostęp do szczegółów zadania Docker: {task_id}")
    
    # Upewnij się, że zadania są załadowane z pliku
    try:
        from docker_tasks_store import load_tasks, get_docker_task
        load_tasks()
        task_info = get_docker_task(task_id)
    except Exception as e:
        logger.error(f"Błąd podczas ładowania zadań Docker: {e}")
        task_info = DOCKER_TASKS.get(task_id)
    
    if not task_info:
        return "Zadanie nie istnieje", 404
    
    # Pobierz podstawowe informacje o zadaniu
    container_id = task_info.get('container_id')
    container_exists = False
    container_status = "Kontener został usunięty po wykonaniu zadania"
    
    # Sprawdź, czy kontener nadal istnieje
    if container_id:
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.ID}}"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                container_exists = True
                # Pobierz status kontenera
                status_result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )
                container_status = status_result.stdout.strip() or "Status nieznany"
            else:
                logger.info(f"Kontener {container_id} nie istnieje już")
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania statusu kontenera: {e}")
            container_status = f"Błąd: {str(e)}"
    
    # Pobierz dodatkowe informacje o kontenerze, jeśli istnieje
    if container_exists:
        try:
            # Pobierz logi kontenera
            logs_result = subprocess.run(
                ["docker", "logs", "--tail", "50", container_id],
                capture_output=True,
                text=True
            )
            task_info['logs'] = logs_result.stdout
        except Exception as e:
            logger.error(f"Błąd podczas pobierania logów: {e}")
            task_info['logs'] = f"Błąd podczas pobierania logów: {str(e)}"
    
    # Przygotuj kontekst dla szablonu
    context = {
        'task_id': task_id,
        'task_info': task_info,
        'container_exists': container_exists,
        'container_status': container_status,
        'execution_result': task_info.get('output', 'Brak wyniku wykonania'),
        'code': task_info.get('code', 'Brak kodu'),
        'timestamp': task_info.get('timestamp', 'Nieznany czas'),
        'is_service': task_info.get('is_service', False)
    }
    
    # Jeśli to serwis, dodaj informacje o URL serwisu niezależnie od tego, czy kontener istnieje
    if task_info.get('is_service'):
        service_url = task_info.get('service_url')
        if service_url:
            context['service_url'] = service_url
            context['service_name'] = task_info.get('service_name', f"Serwis {task_id[:8]}")
            logger.info(f"URL serwisu dla zadania {task_id}: {service_url}")
    
    return render_template('docker_task.html', **context)

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
    container_exists = False
    container_status = "Kontener został usunięty po wykonaniu zadania"
    service_logs = ""
    service_ports = ""
    service_error = ""
    
    if container_id:
        try:
            # Sprawdź, czy kontener istnieje
            exists_result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.ID}}"],
                capture_output=True,
                text=True
            )
            
            if exists_result.stdout.strip():
                container_exists = True
                
                # Status kontenera
                status_result = subprocess.run(
                    ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True
                )
                container_status = status_result.stdout.strip() or "Nieaktywny"
                
                # Logi kontenera
                logs_result = subprocess.run(
                    ["docker", "logs", "--tail", "50", container_id],
                    capture_output=True,
                    text=True
                )
                service_logs = logs_result.stdout
                
                # Pobierz informacje o portach
                ports_result = subprocess.run(
                    ["docker", "port", container_id],
                    capture_output=True,
                    text=True
                )
                service_ports = ports_result.stdout
        except Exception as e:
            service_error = str(e)
            logger.error(f"Błąd podczas pobierania informacji o kontenerze: {e}")
    
    # Pobierz informacje o zadaniu Docker
    task_info = docker_tasks.get(task_id, {})
    
    # Przygotuj kontekst dla szablonu
    context = {
        'task_id': task_id,
        'service_info': service_info,
        'task_info': task_info,
        'container_exists': container_exists,
        'container_status': container_status,
        'service_logs': service_logs,
        'service_ports': service_ports,
        'service_error': service_error,
        'service_url': service_info.get('service_url', ''),
        'service_name': service_info.get('service_name', f"Serwis {task_id[:8]}")
    }
    
    return render_template('service_details.html', **context)

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

@app.route('/conversation/delete/<string:conversation_id>', methods=['POST'])
def delete_conversation(conversation_id):
    """Usuwa konwersację"""
    logger.info(f"Usuwanie konwersacji: {conversation_id}")
    
    try:
        # Sprawdź, czy konwersacja istnieje
        conversation_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
        
        if not os.path.exists(conversation_path):
            logger.warning(f"Konwersacja o ID {conversation_id} nie istnieje w ścieżce: {conversation_path}")
            return jsonify({"error": "Konwersacja nie istnieje"}), 404
        
        # Usuń plik konwersacji
        os.remove(conversation_path)
        logger.info(f"Konwersacja {conversation_id} została usunięta")
        
        return jsonify({"success": True, "message": "Konwersacja została usunięta"})
    
    except Exception as e:
        logger.error(f"Błąd podczas usuwania konwersacji: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/docker/delete/<string:task_id>', methods=['POST'])
def delete_docker_task(task_id):
    """Usuwa zadanie Docker i zatrzymuje kontener, jeśli istnieje"""
    logger.info(f"Usuwanie zadania Docker: {task_id}")
    
    try:
        # Pobierz informacje o zadaniu Docker
        from docker_tasks_store import load_tasks, get_docker_task, DOCKER_TASKS, save_tasks
        load_tasks()
        
        # Logowanie dodatkowych informacji diagnostycznych
        logger.info(f"Dostępne zadania Docker: {list(DOCKER_TASKS.keys())}")
        logger.info(f"Typ ID zadania: {type(task_id)}, Długość: {len(task_id)}")
        logger.info(f"Próba usunięcia zadania Docker o ID: {task_id}")
        
        # Sprawdź, czy zadanie istnieje bezpośrednio w słowniku
        if task_id in DOCKER_TASKS:
            logger.info(f"Zadanie {task_id} znalezione bezpośrednio w słowniku DOCKER_TASKS")
            task_info = DOCKER_TASKS[task_id]
        else:
            # Spróbuj pobrać przez funkcję get_docker_task
            logger.info(f"Zadanie {task_id} nie znalezione bezpośrednio, próba przez get_docker_task")
            task_info = get_docker_task(task_id)
        
        if not task_info:
            logger.error(f"Zadanie {task_id} nie istnieje w systemie")
            return jsonify({
                "error": "Zadanie nie istnieje", 
                "task_id": task_id,
                "available_tasks": list(DOCKER_TASKS.keys())
            }), 404
        
        # Zatrzymaj kontener, jeśli istnieje
        container_id = task_info.get('container_id')
        if container_id and task_info.get('container_exists', False):
            try:
                # Sprawdź, czy kontener istnieje
                result = subprocess.run(
                    ["docker", "inspect", container_id],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Zatrzymaj kontener
                    logger.info(f"Zatrzymywanie kontenera: {container_id}")
                    stop_result = subprocess.run(
                        ["docker", "stop", container_id],
                        capture_output=True,
                        text=True
                    )
                    
                    if stop_result.returncode == 0:
                        logger.info(f"Kontener {container_id} został zatrzymany")
                    else:
                        logger.warning(f"Nie można zatrzymać kontenera {container_id}: {stop_result.stderr}")
            except Exception as e:
                logger.error(f"Błąd podczas zatrzymywania kontenera: {e}")
        
        # Usuń zadanie z słownika
        if task_id in DOCKER_TASKS:
            del DOCKER_TASKS[task_id]
            
            # Zapisz zmiany do pliku
            from docker_tasks_store import save_tasks
            save_tasks()
            
            logger.info(f"Zadanie Docker {task_id} zostało usunięte")
            return jsonify({"success": True, "message": "Zadanie Docker zostało usunięte"})
        else:
            return jsonify({"error": "Zadanie nie istnieje w słowniku"}), 404
    
    except Exception as e:
        logger.error(f"Błąd podczas usuwania zadania Docker: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/docker/delete/<string:task_id>', methods=['GET', 'POST'])
def api_delete_docker_task(task_id):
    """Alternatywny endpoint do usuwania zadań Docker - działa zarówno przez GET jak i POST"""
    logger.info(f"API: Usuwanie zadania Docker: {task_id}")
    
    try:
        # Pobierz informacje o zadaniu Docker
        from docker_tasks_store import load_tasks, DOCKER_TASKS, save_tasks
        load_tasks()  # Upewnij się, że mamy najnowsze dane
        
        logger.info(f"API: Dostępne zadania Docker: {list(DOCKER_TASKS.keys())}")
        
        # Sprawdź, czy zadanie istnieje
        if task_id not in DOCKER_TASKS:
            error_msg = f"API: Zadanie Docker {task_id} nie istnieje w słowniku DOCKER_TASKS"
            logger.warning(error_msg)
            return jsonify({"error": error_msg, "available_tasks": list(DOCKER_TASKS.keys())}), 404
        
        # Pobierz informacje o kontenerze
        task_info = DOCKER_TASKS[task_id]
        container_id = task_info.get('container_id')
        logger.info(f"API: Znaleziono zadanie {task_id} z kontenerem {container_id}")
        
        # Spróbuj zatrzymać kontener, jeśli istnieje
        container_stopped = False
        if container_id:
            try:
                # Sprawdź, czy kontener istnieje
                inspect_result = subprocess.run(
                    ["docker", "inspect", container_id],
                    capture_output=True,
                    text=True
                )
                
                if inspect_result.returncode == 0:
                    # Zatrzymaj kontener
                    logger.info(f"API: Zatrzymywanie kontenera: {container_id}")
                    stop_result = subprocess.run(
                        ["docker", "stop", container_id],
                        capture_output=True,
                        text=True
                    )
                    
                    if stop_result.returncode == 0:
                        logger.info(f"API: Kontener {container_id} został zatrzymany")
                        container_stopped = True
                    else:
                        logger.warning(f"API: Nie można zatrzymać kontenera {container_id}: {stop_result.stderr}")
                else:
                    logger.info(f"API: Kontener {container_id} nie istnieje, pomijanie zatrzymywania")
            except Exception as e:
                logger.error(f"API: Błąd podczas zatrzymywania kontenera: {e}")
        
        # Usuń zadanie ze słownika
        del DOCKER_TASKS[task_id]
        save_tasks()
        
        logger.info(f"API: Zadanie Docker {task_id} zostało usunięte")
        
        # Przekieruj do strony z listą kontenerów lub zwróć JSON
        if request.method == 'GET':
            return redirect('/docker')
        else:
            return jsonify({
                "success": True, 
                "message": f"Zadanie Docker {task_id} zostało usunięte",
                "container_id": container_id,
                "container_stopped": container_stopped
            })
    
    except Exception as e:
        logger.error(f"API: Błąd podczas usuwania zadania Docker: {e}")
        if request.method == 'GET':
            return redirect('/docker')
        else:
            return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/docker/tasks', methods=['GET'])
def api_get_docker_tasks():
    """Endpoint API do pobierania listy wszystkich zadań Docker"""
    logger.info("API: Pobieranie listy wszystkich zadań Docker")
    
    try:
        # Pobierz informacje o zadaniach Docker
        from docker_tasks_store import load_tasks, DOCKER_TASKS
        load_tasks()  # Upewnij się, że mamy najnowsze dane
        
        # Przygotuj listę zadań do zwrócenia
        tasks_list = []
        for task_id, task_info in DOCKER_TASKS.items():
            tasks_list.append({
                "task_id": task_id,
                "container_id": task_info.get('container_id'),
                "timestamp": task_info.get('timestamp'),
                "is_service": task_info.get('is_service', False),
                "container_exists": task_info.get('container_exists', False)
            })
        
        logger.info(f"API: Znaleziono {len(tasks_list)} zadań Docker")
        
        return jsonify({
            "success": True,
            "tasks": tasks_list,
            "task_ids": list(DOCKER_TASKS.keys())
        })
    
    except Exception as e:
        logger.error(f"API: Błąd podczas pobierania zadań Docker: {e}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/logs')
def view_logs():
    """Strona z logami systemu"""
    logger.info("Dostęp do strony z logami systemu")
    
    try:
        # Ścieżka do pliku logów
        log_file = os.path.join(PROJECT_ROOT, 'logs', 'server.log')
        
        # Jeśli plik nie istnieje, utwórz pusty
        if not os.path.exists(log_file):
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            with open(log_file, 'w') as f:
                f.write('Plik logów został utworzony: ' + datetime.now().isoformat() + '\n')
        
        # Pobierz ostatnie 1000 linii logów (można dostosować)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            logs = lines[-1000:]
        
        # Odwróć kolejność, aby najnowsze logi były na górze
        logs.reverse()
        
        return render_template('logs.html', logs=logs)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania logów: {e}")
        return render_template('logs.html', error=str(e), logs=[])

@app.route('/api/logs')
def api_get_logs():
    """API do pobierania logów systemu w formacie JSON"""
    logger.info("API: Pobieranie logów systemu")
    
    try:
        # Ścieżka do pliku logów
        log_file = os.path.join(PROJECT_ROOT, 'logs', 'server.log')
        
        # Jeśli plik nie istnieje, utwórz pusty
        if not os.path.exists(log_file):
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            with open(log_file, 'w') as f:
                f.write('Plik logów został utworzony: ' + datetime.now().isoformat() + '\n')
        
        # Pobierz ostatnie 1000 linii logów (można dostosować)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            logs = lines[-1000:]
        
        # Odwróć kolejność, aby najnowsze logi były na górze
        logs.reverse()
        
        return jsonify({
            "success": True,
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API: Błąd podczas pobierania logów: {e}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

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

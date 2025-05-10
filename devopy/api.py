import sys
from pathlib import Path
from log_db import LogDB
from auto_heal import AutoHealer
import os
import subprocess
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Automatyczny import i instalacja zależności
def ensure_dependencies():
    import importlib
    import subprocess
    import sys
    required = ['flask', 'matplotlib', 'openpyxl', 'requests']
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

ensure_dependencies()

from flask import Flask, request, jsonify, send_from_directory

# Automatyczne tworzenie i aktywacja venv jeśli nie istnieje lub nie jesteśmy w venv
venv_dir = Path(__file__).parent / ".venv"
def in_venv():
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

if not in_venv() or not venv_dir.exists():
    if not venv_dir.exists():
        print("[BOOTSTRAP] Tworzę środowisko wirtualne .venv...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    # Restart w venv jeśli nie jesteśmy w aktywnym venv
    if os.name == "nt":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"
    print(f"[BOOTSTRAP] Restartuję API w środowisku: {python_path}")
    os.execv(str(python_path), [str(python_path)] + sys.argv)

# Automatyczny import i instalacja zależności
def ensure_dependencies():
    import importlib
    import subprocess
    import sys
    required = ['flask', 'matplotlib', 'openpyxl', 'requests']
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

ensure_dependencies()

try:
    from devopy.orchestrator import Orchestrator
except ModuleNotFoundError:
    from orchestrator import Orchestrator

try:
    from flask_swagger_ui import get_swaggerui_blueprint
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-swagger-ui"])
    from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "devopy API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route("/", methods=["GET"])
def index():
    return (
        """
        <h2>devopy API</h2>
        <p>Serwer działa!<br>
        Użyj endpointu <code>/run</code> metodą POST, np.:</p>
        <pre>curl -X POST http://localhost:5050/run -H 'Content-Type: application/json' -d '{"task": "stwórz wykres z pliku excel"}'</pre>
        <p>Więcej przykładów znajdziesz w README.</p>
        <p><a href='/swagger'>Zobacz interaktywną dokumentację Swagger UI</a></p>
        """, 200, {"Content-Type": "text/html; charset=utf-8"}
    )

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

@app.route("/swagger.json")
def swagger_json():
    return jsonify({
        "openapi": "3.0.2",
        "info": {
            "title": "devopy API",
            "version": "1.0",
            "description": "Automatyczna dokumentacja endpointów devopy."
        },
        "paths": {
            "/run": {
                "post": {
                    "summary": "Uruchom zadanie AI",
                    "description": "Przetwarza zadanie tekstowe i wykonuje automatyczne środowisko.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string", "example": "stwórz wykres z pliku excel"}
                                    },
                                    "required": ["task"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Wynik zadania",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "result": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Błąd wykonania",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "error": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })

@app.route("/run", methods=["POST"])
def run_task():
    data = request.get_json(force=True)
    task = data.get("task", "")
    LogDB.log(
        source="api",
        level="info",
        message="/run request",
        request=str(data)
    )
    try:
        orch = Orchestrator()
        result = orch.process_task(task, docker=bool(data.get("docker", False)))
        LogDB.log(
            source="api",
            level="info",
            message="/run response",
            request=str(data),
            response=str(result)
        )
        if isinstance(result, dict) and result.get("plot_file"):
            fname = result["plot_file"]
            download_url = f"/download/{fname}"
            return jsonify({"status": "ok", "result": result, "download_url": download_url})
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        LogDB.log(
            source="api",
            level="error",
            message="/run error",
            request=str(data),
            error=str(e)
        )
        # Automatyczna reakcja naprawcza
        healer = AutoHealer()
        healed = healer.heal_recent_errors(limit=10)
        LogDB.log(
            source="api",
            level="info",
            message="AutoHealer uruchomiony po błędzie",
            response=str(healed)
        )
        return jsonify({"status": "error", "error": str(e), "autoheal": healed}), 500

@app.route("/heal", methods=["POST", "GET"])
def heal_errors():
    healer = AutoHealer()
    healed = healer.heal_recent_errors(limit=20)
    LogDB.log(
        source="api",
        level="info",
        message="/heal uruchomiono",
        response=str(healed)
    )
    return jsonify({"status": "ok", "healed": healed})

@app.route('/download/<filename>')
def download_file(filename):
    from devopy.output_utils import get_output_dir
    out_dir = get_output_dir()
    return send_from_directory(out_dir, filename, as_attachment=True)

@app.route('/logs', methods=['GET'])
def get_logs():
    rows = LogDB.fetch_recent(limit=50)
    logs = [
        {
            "id": row[0],
            "timestamp": row[1],
            "source": row[2],
            "level": row[3],
            "message": row[4],
            "request": row[5],
            "response": row[6],
            "error": row[7],
        }
        for row in rows
    ]
    return jsonify({"logs": logs})

if __name__ == "__main__":
    import os
    import socket
    import subprocess
    import sys
    print("[API] Uruchamiam autoheal_logs.py jako osobny proces...")
    autoheal_proc = subprocess.Popen([
        sys.executable, os.path.join(os.path.dirname(__file__), '..', 'autoheal_logs.py')
    ])
    print(f"[API] Proces autoheal_logs.py uruchomiony (PID={autoheal_proc.pid})")
    def get_free_port(default=5000, fallback=5050):
        # Jeśli port default zajęty, użyj fallback
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", default))
            sock.close()
            return default
        except OSError:
            sock.close()
            return fallback

    port = int(os.environ.get("DEVOPY_PORT", get_free_port()))

    try:
        from auto_diag_import import auto_diag_import
    except ImportError:
        from devopy.auto_diag_import import auto_diag_import
    auto_diag_import(app.run, debug=True, port=port)
    print(f"[INFO] Serwer devopy uruchomiony na porcie {port}")

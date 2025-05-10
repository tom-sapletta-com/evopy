from flask import Flask, request, jsonify
from devopy.orchestrator import Orchestrator

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_task():
    data = request.get_json(force=True)
    task = data.get("task")
    docker = bool(data.get("docker", False))
    if not task:
        return jsonify({"error": "Missing 'task' in request"}), 400
    orch = Orchestrator()
    try:
        orch.process_task(task, docker=docker)
        return jsonify({"status": "ok", "task": task, "docker": docker})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "tasks.json"


# ===============================
# Safe Load
# ===============================
def load_tasks():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


# ===============================
# Safe Save
# ===============================
def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


# ===============================
# Routes
# ===============================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stats")
def stats():
    return render_template("stats.html")


@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    return jsonify(load_tasks())


# ===============================
# Add Task (Safe)
# ===============================
@app.route("/add", methods=["POST"])
def add_task():
    tasks = load_tasks()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    title = data.get("title", "").strip()
    subject = data.get("subject", "").strip()
    date = data.get("date", "")
    start_time = data.get("start_time", "")
    end_time = data.get("end_time", "")

    if not title or not subject:
        return jsonify({"error": "Missing required fields"}), 400

    new_task = {
        "id": max([t.get("id", 0) for t in tasks], default=0) + 1,
        "title": title,
        "subject": subject,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "completed": False
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return jsonify({"status": "success"}), 200


# ===============================
# Toggle Task
# ===============================
@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    tasks = load_tasks()
    found = False

    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = not task.get("completed", False)
            found = True
            break

    if not found:
        return jsonify({"error": "Task not found"}), 404

    save_tasks(tasks)
    return jsonify({"status": "success"}), 200


# ===============================
# Delete Task
# ===============================
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.get("id") != task_id]

    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404

    save_tasks(new_tasks)
    return jsonify({"status": "success"}), 200


# ===============================
# Run
# ===============================
if __name__ == "__main__":
    app.run()
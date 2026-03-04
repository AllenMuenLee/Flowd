import json
import os

def get_procedure(file_path = "procedure.json"):
    with open(file_path, "r") as f:
        return json.load(f)

def save_procedure(procedure, file_path):
    with open(file_path, "w") as f:
        json.dump(procedure, f, indent=4)

def save_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def init_procedure_files(procedure):
    for step_id, data in procedure.items():
        for filename in data['filenames']:
            with open(filename, "w") as f:
                pass
            f.close()

def save_project(project_id, project_path):
    appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
    os.makedirs(appdata_root, exist_ok=True)
    projects_path = os.path.join(appdata_root, "projects.json")

    if os.path.exists(projects_path):
        with open(projects_path, "r", encoding="utf-8") as p:
            try:
                projects = json.load(p)
            except Exception:
                projects = []
    else:
        projects = []

    projects.append({
        "id": project_id,
        "project_root": project_path,
    })

    with open(projects_path, "w", encoding="utf-8") as p:
        json.dump(projects, p, indent=2)

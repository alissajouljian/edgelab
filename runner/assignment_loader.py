import os, yaml

ASSIGNMENTS_DIR = os.environ.get("EDGELAB_ASSIGNMENTS_DIR", "/assignments")

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_assignment(assignment_id: str) -> dict:
    folder = os.path.join(ASSIGNMENTS_DIR, assignment_id)
    meta_path = os.path.join(folder, "assignment.yaml")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Assignment not found: {assignment_id}")
    meta = yaml.safe_load(read_text(meta_path)) or {}
    meta["_folder"] = folder
    return meta

import os, glob
import yaml

ASSIGNMENTS_DIR = os.environ.get("EDGELAB_ASSIGNMENTS_DIR", "/assignments")

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def list_assignments():
    items = []
    # glob is used to search by pattern
    for folder in sorted(glob.glob(os.path.join(ASSIGNMENTS_DIR, "*"))):
        if not os.path.isdir(folder):
            continue
        meta_path = os.path.join(folder, "assignment.yaml")
        if not os.path.exists(meta_path):
            continue
        # read yaml and put in {}
        meta = yaml.safe_load(_read_text(meta_path)) or {}
        items.append(meta)
    return items

def get_assignment(assignment_id: str):
    folder = os.path.join(ASSIGNMENTS_DIR, assignment_id)
    meta_path = os.path.join(folder, "assignment.yaml")
    if not os.path.exists(meta_path):
        return None
    meta = yaml.safe_load(_read_text(meta_path)) or {}
    prompt_path = os.path.join(folder, "prompt.md")
    prompt = _read_text(prompt_path) if os.path.exists(prompt_path) else ""
    # Return templates if present (solution templates)
    template_files = []
    for name in ("solution_template.py", "Main.java.template"):
        p = os.path.join(folder, name)
        if os.path.exists(p):
            template_files.append({"path": name.replace(".template",""), "content": _read_text(p)})
    return meta, prompt, template_files

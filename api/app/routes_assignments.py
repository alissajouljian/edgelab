from fastapi import APIRouter, HTTPException
from .schemas import AssignmentSummary, AssignmentDetail
from .assignments import list_assignments, get_assignment

router = APIRouter()

@router.get("/assignments", response_model=list[AssignmentSummary])
def api_list_assignments():
    metas = list_assignments()
    out = []
    for m in metas:
        out.append({
            "id": m["id"],
            "language": m["language"],
            "entrypoint": m["entrypoint"],
            "time_limit_ms": int(m.get("time_limit_ms", 1500)),
            "memory_limit_mb": int(m.get("memory_limit_mb", 256)),
            "max_output_kb": int(m.get("max_output_kb", 64)),
        })
    return out

@router.get("/assignments/{assignment_id}", response_model=AssignmentDetail)
def api_get_assignment(assignment_id: str):
    got = get_assignment(assignment_id)
    if not got:
        raise HTTPException(status_code=404, detail="Assignment not found")
    meta, prompt, template_files = got
    return {
        "id": meta["id"],
        "language": meta["language"],
        "entrypoint": meta["entrypoint"],
        "time_limit_ms": int(meta.get("time_limit_ms", 1500)),
        "memory_limit_mb": int(meta.get("memory_limit_mb", 256)),
        "max_output_kb": int(meta.get("max_output_kb", 64)),
        "prompt": prompt,
        "template_files": template_files,
    }

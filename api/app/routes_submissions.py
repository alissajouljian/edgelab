import uuid
from fastapi import APIRouter, Depends, HTTPException
from requests import RequestException
from sqlalchemy.orm import Session
from .db import get_db, engine
from .models import Submission, SubmissionFile, SubmissionResult
from .schemas import SubmissionCreate, SubmissionCreated, SubmissionStatus
from .assignments import get_assignment
from .db import Base
from .llm_client import generate_feedback
from .schemas import SubmissionFeedback, SubmissionFeedbackRequest

router = APIRouter()

# Create tables on startup (simple local)
Base.metadata.create_all(bind=engine)

@router.post("/submissions", response_model=SubmissionCreated)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    got = get_assignment(payload.assignment_id)
    if not got:
        raise HTTPException(status_code=404, detail="Assignment not found")
    meta, _prompt, _templates = got
    sub_id = str(uuid.uuid4())
    submission = Submission(
        id=sub_id,
        assignment_id=payload.assignment_id,
        language=meta["language"],
        status="created",
    )
    db.add(submission)
    for f in payload.files:
        db.add(SubmissionFile(submission_id=sub_id, path=f.path, content=f.content))
    db.commit()
    return {"id": sub_id, "status": "created"}

@router.post("/submissions/{submission_id}/evaluate")
def queue_evaluation(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.status in ("running",):
        raise HTTPException(status_code=409, detail="Submission already running")
    sub.status = "queued"
    db.commit()
    return {"id": sub.id, "status": sub.status}

@router.get("/submissions/{submission_id}", response_model=SubmissionStatus)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    res = sub.result
    out = {
        "id": sub.id,
        "assignment_id": sub.assignment_id,
        "language": sub.language,
        "status": sub.status,
    }
    if res:
        logs = res.logs or ""
        if "=== Hidden run ===" in logs:
            logs = logs.split("=== Hidden run ===")[0].rstrip()

        out.update({
            "score": res.score,
            "public": res.public_json,
            "logs": logs,
            "runtime_ms": res.runtime_ms,
        })

    return out


@router.post("/submissions/{submission_id}/feedback", response_model=SubmissionFeedback)
def get_feedback(submission_id: str, payload: SubmissionFeedbackRequest | None = None, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Load assignment prompt (safe info)
    got = get_assignment(sub.assignment_id)
    if not got:
        raise HTTPException(status_code=404, detail="Assignment not found")
    meta, prompt, _templates = got

    # Collect submitted files (safe info: user provided)
    files = sub.files or []
    code_text = "\n\n".join([f"FILE: {f.path}\n{f.content}" for f in files])

    # Only include PUBLIC info. Do NOT include hidden tests.
    # If result exists, include only "public_json" (already user-visible).
    public_summary = ""
    if sub.result:
        public_summary = str(sub.result.public_json)

    # Build prompt that avoids leakage
    llm_prompt = f"""
You are a code reviewer for a learning platform.
Give helpful, actionable feedback. Do NOT mention or guess hidden tests.

Assignment:
{prompt}

Language: {meta.get("language")}

User submission:
{code_text}

Public test summary (user-visible only):
{public_summary}

Return feedback as plain text with:
- 3-6 key issues (if any)
- suggested improvements
- optional complexity/performance notes
""".strip()

    model = payload.model if payload else None
    try:
        feedback = generate_feedback(llm_prompt, model)
    except RequestException as e:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"id": sub.id, "feedback": feedback}

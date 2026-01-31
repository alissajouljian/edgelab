import os, time, traceback
from sqlalchemy import select
from db import engine, SessionLocal, Base
from  models import Submission, SubmissionResult
from  assignment_loader import load_assignment
from  sandbox import evaluate_submission

POLL = float(os.environ.get("EDGELAB_POLL_INTERVAL_SEC", "1"))

# Ensure tables exist (API also creates, but runner may start first)
Base.metadata.create_all(bind=engine)

def main():
    print("Runner started. Polling for queued submissions...")
    while True:
        try:
            run_once()
        except Exception as e:
            print("Runner loop error:", e)
            traceback.print_exc()
        time.sleep(POLL)

def run_once():
    with SessionLocal() as db:
        sub = db.execute(
            select(Submission).where(Submission.status == "queued").order_by(Submission.created_at.asc()).limit(1)
        ).scalars().first()

        if not sub:
            return

        sub.status = "running"
        db.commit()

        try:
            assignment = load_assignment(sub.assignment_id)
            time_limit_ms = int(assignment.get("time_limit_ms", 1500))
            memory_limit_mb = int(assignment.get("memory_limit_mb", 256))
            max_output_kb = int(assignment.get("max_output_kb", 64))
            scoring = assignment.get("scoring", {"public":50, "hidden":50})
            entrypoint = assignment.get("entrypoint")

            files = [(f.path, f.content) for f in sub.files]
            score, public, hidden, logs, runtime_ms = evaluate_submission(
                language=sub.language,
                assignment_folder=assignment["_folder"],
                entrypoint=entrypoint,
                files=files,
                time_limit_ms=time_limit_ms,
                memory_limit_mb=memory_limit_mb,
                max_output_kb=max_output_kb,
                scoring=scoring,
            )

            # Upsert result
            existing = db.get(SubmissionResult, sub.id)
            if existing:
                existing.score = score
                existing.public_json = public
                existing.hidden_json = hidden
                existing.logs = logs
                existing.runtime_ms = runtime_ms
            else:
                db.add(SubmissionResult(
                    submission_id=sub.id,
                    score=score,
                    public_json=public,
                    hidden_json=hidden,
                    logs=logs,
                    runtime_ms=runtime_ms,
                ))
            sub.status = "done"
            db.commit()
            print(f"Finished submission {sub.id} score={score}")

        except Exception as e:
            sub.status = "failed"
            # Save minimal failure result (no internal stack)
            existing = db.get(SubmissionResult, sub.id)
            if not existing:
                db.add(SubmissionResult(
                    submission_id=sub.id,
                    score=0,
                    public_json={"passed": False, "feedback":[{"message":"Runner error"}]},
                    hidden_json={"passed": False, "note":"Runner error"},
                    logs="Runner error occurred. Check server logs.",
                    runtime_ms=0,
                ))
            db.commit()
            print(f"Submission {sub.id} failed:", e)
            traceback.print_exc()

if __name__ == "__main__":
    main()

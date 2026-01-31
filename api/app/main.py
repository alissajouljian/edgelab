from fastapi import FastAPI
from .routes_assignments import router as assignments_router
from .routes_submissions import router as submissions_router

# API start
# Swagger is the API UI that FastAPI automatically starts when you create a FastAPI app.
app = FastAPI(title="EdgeLab v0.1")

app.include_router(assignments_router)
app.include_router(submissions_router)

@app.get("/")
def root():
    return {"name": "EdgeLab v0.1", "status": "ok"}

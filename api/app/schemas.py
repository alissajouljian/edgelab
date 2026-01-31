from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing import Optional

class SubmissionFeedback(BaseModel):
    id: str
    feedback: str

class SubmissionFeedbackRequest(BaseModel):
    model: Optional[str] = None

class AssignmentSummary(BaseModel):
    id: str
    language: str
    entrypoint: str
    time_limit_ms: int
    memory_limit_mb: int
    max_output_kb: int

class AssignmentDetail(AssignmentSummary):
    prompt: str
    template_files: List[Dict[str, str]] = Field(default_factory=list)

class FileIn(BaseModel):
    path: str
    content: str

class SubmissionCreate(BaseModel):
    assignment_id: str
    files: List[FileIn]

class SubmissionCreated(BaseModel):
    id: str
    status: str

class SubmissionStatus(BaseModel):
    id: str
    assignment_id: str
    language: str
    status: str
    score: Optional[int] = None
    public: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None
    runtime_ms: Optional[int] = None

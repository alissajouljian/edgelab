from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    assignment_id = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    files = relationship("SubmissionFile", back_populates="submission")
    result = relationship("SubmissionResult", back_populates="submission", uselist=False)

class SubmissionFile(Base):
    __tablename__ = "submission_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False, index=True)
    path = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    submission = relationship("Submission", back_populates="files")

class SubmissionResult(Base):
    __tablename__ = "submission_results"
    submission_id = Column(String, ForeignKey("submissions.id"), primary_key=True)
    score = Column(Integer, nullable=False, default=0)
    public_json = Column(JSON, nullable=False)
    hidden_json = Column(JSON, nullable=False)
    logs = Column(Text, nullable=False, default="")
    runtime_ms = Column(Integer, nullable=False, default=0)
    submission = relationship("Submission", back_populates="result")

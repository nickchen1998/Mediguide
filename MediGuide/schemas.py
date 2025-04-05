from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class Symptom(BaseModel):
    id: Field(alias="_id")
    subject_id: int
    subject: str
    symptom: str
    question: str
    gender: str
    question_time: datetime
    answer: str
    department: str
    answer_time: datetime
    summary: Optional[str] = None
    summary_embedding: Optional[List[float]] = None

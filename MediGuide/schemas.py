from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from bson import ObjectId


class Symptom(BaseModel):
    id: ObjectId = Field(alias="_id")
    subject_id: int
    subject: str
    symptom: str
    question: str
    question_embeddings: Optional[List[float]] = None
    gender: str
    question_time: datetime
    answer: str
    department: str
    answer_time: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

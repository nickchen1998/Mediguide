from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from bson import ObjectId
from datetime import datetime


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

    @field_validator("id", mode="before")
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            return ObjectId(v)
        raise TypeError("Invalid type for ObjectId")

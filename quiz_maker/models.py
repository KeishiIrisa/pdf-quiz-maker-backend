from pydantic import BaseModel
from typing import List

class Source(BaseModel):
    text: str
    page: int
    file_path: str
    score: float

class Quiz(BaseModel):
    question: str
    answer: str
    description: str
    sources: List[Source]

from typing import List

from pydantic import BaseModel

from .ai_service import Source


class GenerateQuizRequest(BaseModel):
    education_resources_id: str
    learning_content: str


class Quiz(BaseModel):
    question: str
    answer: str
    description: str
    sources: List[Source]

from pydantic import BaseModel
from typing import List, Dict

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
    
class EducationResource(BaseModel):
    subject: str
    learning_documents_ids: List[str]
    quizzes_ids: List[str] # MongoDB's Objectid(str)
    
class LearningDocument(BaseModel):
    title: str
    content: str
    metadata: Dict[str, str]

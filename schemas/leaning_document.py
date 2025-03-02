from typing import Dict

from pydantic import BaseModel


class LearningDocumentCreate(BaseModel):
    title: str
    content: str
    metadata: Dict[str, str]

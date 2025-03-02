from pydantic import BaseModel


class EducationResourceCreate(BaseModel):
    subject: str
    description: str = ""

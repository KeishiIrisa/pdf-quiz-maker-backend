from pydantic import BaseModel


class Html(BaseModel):
    html: str


class Source(BaseModel):
    text: str
    page: int
    file_path: str
    score: float

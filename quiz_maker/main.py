from fastapi import FastAPI, UploadFile, File, Form
from quiz_maker.pdf_to_markdown import convert_pdf_to_makrdown
from quiz_maker.openai_utils import answer_question_from_pdf
from dotenv import load_dotenv
import openai
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Hello keishi!"}

@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...), learning_content: str = Form(...)):
    answer = answer_question_from_pdf(file, learning_content)
    return {"filename": file.filename, "answer": answer}


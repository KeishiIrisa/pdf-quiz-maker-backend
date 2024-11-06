from fastapi import FastAPI, UploadFile, File, Form
from quiz_maker.openai_utils import answer_question_from_pdf
from quiz_maker.models import Quiz
from quiz_maker.mongodb_utils import insert_quiz
from dotenv import load_dotenv
from pymongo import MongoClient
import openai
import os
import json

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
print(f"MongoDB URI: {mongodb_uri}") 

client = MongoClient(mongodb_uri)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Hello keishi!"}

@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...), learning_content: str = Form(...)):
    answer = answer_question_from_pdf(file, learning_content)
    return {"filename": file.filename, "answer": answer}

@app.get("/test/insert_quiz")
async def test_insert_quiz():
    with open('quiz_maker/quizzes_sample.json', 'r', encoding='utf-8') as file:
        quiz_data = json.load(file)
    
    print(type(quiz_data))

    inserted_id = insert_quiz(quiz_data)
    return {"inserted_id": inserted_id}

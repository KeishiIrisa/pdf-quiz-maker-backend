import os
import json

from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel
import openai
from fastapi import FastAPI, UploadFile, File, Form

from quiz_maker.openai_utils import answer_question_by_education_resources_id
from quiz_maker.models import Quiz
from quiz_maker.mongodb_utils import insert_quiz, fetch_all_quizzes, insert_education_resource, add_learning_content_to_resource
from quiz_maker.astradb_utils import save_vectors_to_astra
from quiz_maker.data_processing_utils import process_pdf_file, process_from_llama_docs_to_text

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
print(f"MongoDB URI: {mongodb_uri}") 

client = MongoClient(mongodb_uri)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# defining requestbody
class EducationResourceCreate(BaseModel):
    subject: str
    
class GenerateQuizRequest(BaseModel):
    education_resources_id: str
    learning_content: str

@app.get("/")
def read_root():
    return {"Message": "Hello keishi!"}

# TODO ここをuploadfileではなく、education_resources_idとlearningcontentのみを受け取るように仕様変更する
@app.post("/generate_quiz")
async def generate_quiz(request: GenerateQuizRequest):
    answer = answer_question_by_education_resources_id(request.education_resources_id, request.learning_content)
    return {"answer": answer}

@app.get("/quizzes/")
async def get_all_quizzes():
    quizzes = fetch_all_quizzes()
    return quizzes

# education_resources
@app.post("/education_resources")
async def create_education_resource(resource: EducationResourceCreate):
    education_resource = {
        "subject": resource.subject,
        "learning_contents": [],
        "quizzes_ids": []
    }
    inserted_id = insert_education_resource(education_resource)
    return {"inserted_id": inserted_id}


@app.put("/education_resources/{education_resource_id}/uploadfile")
async def update_learning_content_from_file(education_resource_id: str, file: UploadFile = File(...)):
    llama_docs = process_pdf_file(file)
    learning_content = process_from_llama_docs_to_text(llama_docs, education_resource_id)
    
    # save learning content in mongodb
    success_db = add_learning_content_to_resource(education_resource_id, learning_content)
    
    if success_db:
        # save vector to astraDB
        save_vectors_to_astra(llama_docs)
    return {"filename": file.filename, "success": success_db}
    

@app.get("/test/insert_quiz")
async def test_insert_quiz():
    with open('quiz_maker/quizzes_sample.json', 'r', encoding='utf-8') as file:
        quiz_data = json.load(file)
    
    print(type(quiz_data))

    inserted_id = insert_quiz(quiz_data)
    return {"inserted_id": inserted_id}


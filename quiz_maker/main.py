import os
import json

from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
import openai
from fastapi import FastAPI, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse

from quiz_maker.openai_utils import generate_quiz_by_education_resources_id
from quiz_maker.models import Quiz
from quiz_maker.mongodb_utils import insert_quiz, fetch_all_quizzes, fetch_education_resource_by_id, fetch_quizzes_by_ids, insert_education_resource, add_learning_content_to_resource
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

class QuizIdsRequest(BaseModel):
    quiz_ids: List[str]

@app.get("/")
def read_root():
    return {"Message": "Hello keishi!"}

@app.post("/quiz")
async def generate_quiz(request: GenerateQuizRequest):
    try:
        quiz = generate_quiz_by_education_resources_id(request.education_resources_id, request.learning_content).model_dump()
        return JSONResponse(content={"quiz": quiz}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/quizzes")
async def get_all_quizzes():
    quizzes = fetch_all_quizzes()
    return quizzes

@app.post("/quizzes")
async def get_quizzes_by_ids(quiz_ids: QuizIdsRequest):
    quizzes = fetch_quizzes_by_ids(quiz_ids.quiz_ids)
    return quizzes

# education_resources
@app.get("/education-resources/{education_resources_id}")
async def get_education_resource_by_id(education_resources_id: str):
    education_resource = fetch_education_resource_by_id(education_resources_id)
    return education_resource

@app.post("/education-resources")
async def create_education_resource(resource: EducationResourceCreate):
    education_resource = {
        "subject": resource.subject,
        "learning_contents": [],
        "quizzes_ids": []
    }
    inserted_id = insert_education_resource(education_resource)
    return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)


@app.put("/education-resources/{education_resource_id}/uploadfile", status_code=status.HTTP_204_NO_CONTENT)
async def update_learning_content_from_file(education_resource_id: str, file: UploadFile = File(...)):
    llama_docs = process_pdf_file(file)
    learning_content = process_from_llama_docs_to_text(llama_docs, education_resource_id)
    
    # save learning content in mongodb
    success_db = add_learning_content_to_resource(education_resource_id, learning_content)
    
    if success_db:
        # save vector to astraDB
        save_vectors_to_astra(llama_docs)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save learning content to MongoDB")
    

# @app.get("/test/insert-quiz")
# async def test_insert_quiz():
#     with open('quiz_maker/quizzes_sample.json', 'r', encoding='utf-8') as file:
#         quiz_data = json.load(file)
    
#     print(type(quiz_data))

#     inserted_id = insert_quiz(quiz_data)
#     return {"inserted_id": inserted_id}


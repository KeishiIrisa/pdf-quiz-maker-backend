import os
import json

from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Dict
import openai
from fastapi import FastAPI, UploadFile, File, status, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from quiz_maker.openai_utils import generate_quiz_by_education_resources_id, generate_html_from_text
from quiz_maker.models import Quiz
from quiz_maker.mongodb_utils import fetch_education_resources, fetch_education_resource_by_id, fetch_quiz_by_id, insert_education_resource, add_learning_document_id_to_resource, insert_learning_document, fetch_learning_document_by_id
from quiz_maker.astradb_utils import save_vectors_to_astra
from quiz_maker.data_processing_utils import process_pdf_file, process_from_llama_docs_to_text, process_markdown_to_html

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
print(f"MongoDB URI: {mongodb_uri}") 

client = MongoClient(mongodb_uri)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://pdf-quiz-maker.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defining requestbody
class EducationResourceCreate(BaseModel):
    subject: str
    description: str = ""
    
class LearningDocumentCreate(BaseModel):
    title: str
    content: str
    metadata: Dict[str, str]
    
class GenerateQuizRequest(BaseModel):
    education_resources_id: str
    learning_content: str

class QuizIdsRequest(BaseModel):
    quiz_ids: List[str]
    
class MarkdownRequest(BaseModel):
    markdown: str

@app.get("/")
def read_root():
    return {"Message": "Hello keishi!"}

@app.post("/quiz")
async def generate_quiz(request: GenerateQuizRequest):
    try:
        quiz = generate_quiz_by_education_resources_id(request.education_resources_id, request.learning_content).model_dump()
        return JSONResponse(content=quiz, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.get("/quizzes")
# async def get_all_quizzes():
#     quizzes = fetch_all_quizzes()
#     return quizzes

@app.get("/quiz/{quiz_id}")
async def get_quiz_by_id(quiz_id: str):
    quiz = fetch_quiz_by_id(quiz_id)
    return quiz

# learning_documents
# @app.post("/learning-document")
# async def create_learning_document(resource: LearningDocumentCreate):
#     learning_document = {
#         "title": resource.title,
#         "content": resource.content,
#         "metadata": resource.metadata
#     }
    
#     inserted_id = insert_learning_document(learning_document)
#     return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)

@app.get("/learning-document/{learning_document_id}")
async def get_learning_documents(learning_document_id: str):
    learning_document = fetch_learning_document_by_id(learning_document_id)
    return learning_document
    

# education_resources
@app.get("/education-resources")
async def get_education_resources():
    education_resources = fetch_education_resources()
    return education_resources

@app.get("/education-resources/{education_resources_id}")
async def get_education_resource_by_id(education_resources_id: str):
    education_resource = fetch_education_resource_by_id(education_resources_id)
    return education_resource

@app.post("/education-resources")
async def create_education_resource(resource: EducationResourceCreate):
    education_resource = {
        "subject": resource.subject,
        "description": resource.description,
        "learning_documents_ids": [],
        "quizzes_ids": []
    }
    inserted_id = insert_education_resource(education_resource)
    return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)


@app.put("/education-resources/{education_resource_id}/uploadfile", status_code=status.HTTP_204_NO_CONTENT)
async def update_learning_content_from_file(education_resource_id: str, file: UploadFile = File(...)):
    llama_docs = process_pdf_file(file)
    raw_text = process_from_llama_docs_to_text(llama_docs, education_resource_id)
    learning_document = {
        "title": file.filename,
        "content": generate_html_from_text(raw_text),
        "metadata": {}
    }
    
    # TODO make the below functions if the other function fails, the other function will fail
    
    # save learning_document in mongodb and get inserted_id
    learning_document_inserted_id = insert_learning_document(learning_document)
    
    if not learning_document_inserted_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save learning document to learning document collection")
        
    # save learning document id to education resource 
    success_db = add_learning_document_id_to_resource(education_resource_id, learning_document_inserted_id)
    
    if success_db:
        # save vector to astraDB
        save_vectors_to_astra(llama_docs)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save learning_document_inserted_id to education_resource")
    
@app.post("/test/markdown")
async def change_to_html(request: MarkdownRequest):
    html = process_markdown_to_html(request.markdown)
    return {"html": html}

@app.get("/test/html")
async def change_to_html():
    raw_text = """
    経済思想概論1 §古代ギリシャのアテネは，商業の発展や他都市との覇権争いのなかで，様々な政治改革を経験する。§プラトンは『国家』で，政治体制の変化を理論化し，知性によって軍人や商人を管理する理想的な国家像を示す。政治指導者の私有財産を禁止するよう提言。§アリストテレスは，プラトンの急進的な考えを批判。「目的」に対応した「自然」な社会体制を議論する。ただし，商業には批判的。
    """
    return {"html": generate_html_from_text(raw_text)}

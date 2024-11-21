import os
from typing import Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client.get_database("pdf_quiz_maker_db")
quizzes_collection = db["quizzes"]
education_resources_collection = db["education_resources"]


# quizzes process
def insert_quiz(quiz: Dict):
    result = quizzes_collection.insert_one(quiz)
    return str(result.inserted_id)

def fetch_all_quizzes() -> List[Dict]:
    results = quizzes_collection.find()
    quizzes = []
    for result in results:
        result["_id"] = str(result["_id"])  # ObjectIdを文字列に変換
        quizzes.append(result)
    return quizzes


# education_resources process
def insert_education_resource(education_resource: Dict):
    result = education_resources_collection.insert_one(education_resource)
    return str(result.inserted_id)

def add_learning_content_to_resource(education_resource_id: str, learning_content: str):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resource_id)},
        {"$push": {"learning_contents": learning_content}}
    )
    return result.modified_count > 0

def add_quizzes_to_resource(education_resources_id: str, quizzes_id: str):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resources_id)},
        {"$push": {"quizzes_ids": quizzes_id}}
    )
    return result.modified_count > 0

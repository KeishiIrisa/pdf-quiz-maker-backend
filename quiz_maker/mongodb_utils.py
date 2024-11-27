import os
from typing import Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from quiz_maker.models import LearningDocument

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client.get_database("pdf_quiz_maker_db")
quizzes_collection = db["quizzes"]
education_resources_collection = db["education_resources"]
learning_documents_collection = db["learning_documents"]

def change_objectid_to_str(result):
    result["_id"] = str(result["_id"])
    return result


# quizzes process
def insert_quiz(quiz: Dict):
    result = quizzes_collection.insert_one(quiz)
    return str(result.inserted_id)

def fetch_all_quizzes() -> List[Dict]:
    results = quizzes_collection.find()
    return [change_objectid_to_str(result) for result in results]

def fetch_quiz_by_id(quiz_id: str):
    object_id = ObjectId(quiz_id)
    result = quizzes_collection.find_one({"_id": object_id})
    if result:
        return change_objectid_to_str(result)
    return None

# learning_document
def insert_learning_document(learning_document: Dict):
    result = learning_documents_collection.insert_one(learning_document)
    return str(result.inserted_id)

def fetch_learning_document_by_id(learning_document_id: str):
    result = learning_documents_collection.find_one({"_id": ObjectId(learning_document_id)})
    if result:
        result["_id"] = str(result["_id"])
    return result

# education_resources process
def insert_education_resource(education_resource: Dict):
    result = education_resources_collection.insert_one(education_resource)
    return str(result.inserted_id)

def add_learning_document_id_to_resource(education_resource_id: str, learning_document_id: str):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resource_id)},
        {"$push": {"learning_documents_ids": learning_document_id}}
    )
    return result.modified_count > 0

def add_quizzes_to_resource(education_resources_id: str, quizzes_id: str):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resources_id)},
        {"$push": {"quizzes_ids": quizzes_id}}
    )
    return result.modified_count > 0


def fetch_education_resource_by_id(education_resources_id: str):
    result = education_resources_collection.find_one({"_id": ObjectId(education_resources_id)})
    if result:
        result["_id"] = str(result["_id"])
    return result

def fetch_education_resources() -> List[Dict]:
    results = education_resources_collection.find()
    return [change_objectid_to_str(result) for result in results]

import os
from typing import Dict

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client.get_database("pdf_quiz_maker_db")
quizzes_collection = db["quizzes"]
education_resources_collection = db["education_resources"]
learning_documents_collection = db["learning_documents"]


# quiz
def insert_quiz(quiz: Dict):
    result = quizzes_collection.insert_one(quiz)
    return str(result.inserted_id)


def fetch_all_quizzes():
    return quizzes_collection.find()


def fetch_quiz_by_id(quiz_id: ObjectId):
    return quizzes_collection.find_one({"_id": quiz_id})


# learning_document
def insert_learning_document(learning_document: Dict):
    result = learning_documents_collection.insert_one(learning_document)
    return str(result.inserted_id)


def fetch_learning_document_by_id(learning_document_id: str):
    return learning_documents_collection.find_one(
        {"_id": ObjectId(learning_document_id)}
    )


# education_resources process
def insert_education_resource(education_resource: Dict):
    return education_resources_collection.insert_one(education_resource)


def add_learning_document_id_to_resource(
    education_resource_id: str, learning_document_id: str
):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resource_id)},
        {"$push": {"learning_documents_ids": learning_document_id}},
    )
    return result


def add_quizzes_to_resource(education_resources_id: str, quizzes_id: str):
    result = education_resources_collection.update_one(
        {"_id": ObjectId(education_resources_id)},
        {"$push": {"quizzes_ids": quizzes_id}},
    )
    return result


def fetch_education_resource_by_id(education_resources_id: str):
    return education_resources_collection.find_one(
        {"_id": ObjectId(education_resources_id)}
    )


def fetch_education_resources():
    return education_resources_collection.find()

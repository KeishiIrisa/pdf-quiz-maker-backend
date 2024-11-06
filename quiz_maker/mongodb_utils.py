import os
from typing import Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client.get_database("pdf_quiz_maker_db")
quizzes_collection = db["quizzes"]


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

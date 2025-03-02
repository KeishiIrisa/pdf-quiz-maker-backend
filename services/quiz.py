from bson import ObjectId

from db import mongodb_utils
from utils import data_processing_utils, openai_utils


def get_all_quizzes():
    results = mongodb_utils.fetch_all_quizzes()
    return [data_processing_utils.change_objectid_to_str(result) for result in results]


def get_quiz_by_id(quiz_id: str):
    result = mongodb_utils.fetch_quiz_by_id(ObjectId(quiz_id))
    if result:
        return data_processing_utils.change_objectid_to_str(result)
    return None


def add_quizzes_to_resource(education_resources_id: str, quizzes_id: str):
    result = mongodb_utils.add_quizzes_to_resource(education_resources_id, quizzes_id)
    return result.modified_count > 0


def generate_quiz_by_education_resources_id(
    education_resources_id: str, learning_content: str
):
    try:
        quiz = openai_utils.generate_quiz_by_education_resources_id(
            education_resources_id, learning_content
        )

        inserted_quiz_id = mongodb_utils.insert_quiz(quiz.model_dump())
        mongodb_utils.add_quizzes_to_resource(education_resources_id, inserted_quiz_id)

        return quiz
    except Exception as e:
        raise Exception(str(e))

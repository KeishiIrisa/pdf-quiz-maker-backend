from db import mongodb_utils


def get_learning_document_by_id(learning_document_id: str):
    result = mongodb_utils.fetch_learning_document_by_id(learning_document_id)
    if result:
        result["_id"] = str(result["_id"])
    return result

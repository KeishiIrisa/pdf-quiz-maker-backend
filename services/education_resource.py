from typing import Dict

from fastapi import UploadFile

from db import astradb_utils, mongodb_utils
from utils import data_processing_utils, openai_utils


def get_education_resources():
    results = mongodb_utils.fetch_education_resources()
    return [data_processing_utils.change_objectid_to_str(result) for result in results]


def get_education_resource_by_id(education_resources_id: str):
    result = mongodb_utils.fetch_education_resource_by_id(education_resources_id)
    if result:
        result["_id"] = str(result["_id"])
    return result


def insert_education_resource(education_resource: Dict):
    result = mongodb_utils.insert_education_resource(education_resource)
    return str(result.inserted_id)


def add_learning_document_id_to_resource(
    education_resource_id: str, learning_document_id: str
):
    result = mongodb_utils.add_learning_document_id_to_resource(
        education_resource_id, learning_document_id
    )
    return result.modified_count > 0


def update_learning_content_from_file(education_resource_id: str, file: UploadFile):
    llama_docs = data_processing_utils.process_pdf_file(file)
    raw_text = data_processing_utils.process_from_llama_docs_to_text(
        llama_docs, education_resource_id
    )
    learning_document = {
        "title": file.filename,
        "content": openai_utils.generate_html_from_text(raw_text),
        "metadata": {},
    }

    learning_document_inserted_id = mongodb_utils.insert_learning_document(
        learning_document
    )

    if not learning_document_inserted_id:
        raise Exception("Fail to insert learning document")

    save_success = mongodb_utils.add_learning_document_id_to_resource(
        education_resource_id, learning_document_inserted_id
    )

    if save_success:
        astradb_utils.save_vectors_to_astra(llama_docs)
    else:
        raise Exception("Fail to save learning document id to education resource")

from fastapi import APIRouter

import services.learning_document as learning_document_usecase

router = APIRouter(
    prefix="/learning-document",
    tags=["learning-document"],
)


@router.get("/{learning_document_id}")
def get_learning_documents(learning_document_id: str):
    learning_document = learning_document_usecase.get_learning_document_by_id(
        learning_document_id
    )
    return learning_document

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

import services.education_resource as education_resource_usecase
from schemas.education_resource import EducationResourceCreate

router = APIRouter(
    prefix="/education-resource",
    tags=["education-resource"],
)


@router.get("/")
def get_education_resources():
    education_resources = education_resource_usecase.get_education_resources()
    return education_resources


@router.post("/")
def create_education_resource(resource: EducationResourceCreate):
    education_resource = {
        "subject": resource.subject,
        "description": resource.description,
        "learning_documents_ids": [],
        "quizzes_ids": [],
    }
    inserted_id = education_resource_usecase.insert_education_resource(
        education_resource
    )
    return JSONResponse(
        content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED
    )


@router.get("/{education_resources_id}")
def get_education_resource_by_id(education_resources_id: str):
    education_resource = education_resource_usecase.get_education_resource_by_id(
        education_resources_id
    )
    return education_resource


@router.put(
    "/{education_resource_id}/uploadfile", status_code=status.HTTP_204_NO_CONTENT
)
async def update_learning_content_from_file(
    education_resource_id: str, file: UploadFile = File(...)
):
    try:
        education_resource_usecase.update_learning_content_from_file(
            education_resource_id, file
        )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

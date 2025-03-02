from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

import services.quiz as quiz_usecase
from schemas.quiz import GenerateQuizRequest

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)


@router.get("/")
def get_all_quizzes():
    quizzes = quiz_usecase.get_all_quizzes()
    return quizzes


@router.post("/")
async def generate_quiz(request: GenerateQuizRequest):
    try:
        quiz = quiz_usecase.generate_quiz_by_education_resources_id(
            request.education_resources_id, request.learning_content
        ).model_dump()
        return JSONResponse(content=quiz, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{quiz_id}")
def get_quiz_by_id(quiz_id: str):
    quiz = quiz_usecase.get_quiz_by_id(quiz_id)
    return quiz

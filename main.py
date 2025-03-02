from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import education_resource, learning_document, quiz

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://pdf-quiz-maker.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Content-Language",
        "Content-Length",
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "Origin",
    ],
)

router = APIRouter()
router.include_router(learning_document.router)
router.include_router(education_resource.router)
router.include_router(quiz.router)
app.include_router(router)

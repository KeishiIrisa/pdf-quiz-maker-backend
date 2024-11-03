# Setup

## Create docker image

```
docker build -t pdf-quiz-maker-backend:0.1.0 .
```

## Run main application

```
uvicorn pdf_quiz_maker_backend.main:app --reload
```

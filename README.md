# Setup

## Create docker image

```
docker build -t pdf-quiz-maker-backend:0.1.0 .
```

## Run application in docker container

```
docker compose up --build
```

## Run main application

```
uvicorn pdf_quiz_maker_backend.main:app --reload
```

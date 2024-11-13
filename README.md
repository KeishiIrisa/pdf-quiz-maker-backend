# Setup

## Create docker image

```
docker build -t quiz_maker:0.1.0 .
```

## Run application in docker container

```
docker compose up --build
```

## Run main application

```
uvicorn quiz_maker.main:app --reload
```

## directory graph in docker container

```
/app
├── pyproject.toml
└── quiz_maker
    ├── __init__.py
    ├── main.py
    └── その他のファイルやディレクトリ
```

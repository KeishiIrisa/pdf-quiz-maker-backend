FROM python:3.11

ENV PYTHONUNBUFFERED True \
    POETRY_VIRTUALENVS_CREATE false \
    PORT 8080

RUN apt-get update && apt-get install -y curl poppler-utils git openssh-client

WORKDIR /app

ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -  && poetry config virtualenvs.create false

COPY pyproject.toml ./

RUN poetry install --no-root

COPY . /app/

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

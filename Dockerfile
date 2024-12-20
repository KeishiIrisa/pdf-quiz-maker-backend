FROM python:3.11

ENV PYTHONUNBUFFERED True \
    POETRY_VIRTUALENVS_CREATE false \
    PORT 8080

RUN apt-get update && apt-get install -y curl poppler-utils git openssh-client

# Clarify working directory is "/app" in this sentence
WORKDIR /app

ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -  && poetry config virtualenvs.create false

COPY pyproject.toml ./

#RUN poetry install --without dev
RUN poetry install --no-root

COPY ./quiz_maker ./quiz_maker

EXPOSE 8080

# # product
# CMD ["uvicorn", "quiz_maker.main:app", "--host", "0.0.0.0", "--port", "8080"]

# dev
CMD ["uvicorn", "quiz_maker.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

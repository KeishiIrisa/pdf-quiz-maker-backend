FROM python:3.11

ENV PYTHONUNBUFFERED True \
    APP_HOME /app \
    POETRY_VIRTUALENVS_CREATE false \
    PORT 8000

RUN apt-get update && apt-get install -y curl poppler-utils git openssh-client

WORKDIR $APP_HOME

ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -  && poetry config virtualenvs.create false

COPY pyproject.toml ./

#RUN poetry install --without dev
RUN poetry install --no-root

COPY ./pdf_quiz_maker_backend ./pdf_quiz_maker_backend

# CMD exec uvicorn pdf_quiz_maker_backend.main:app --host=0.0.0.0 --port=$PORT
CMD uvicorn pdf_quiz_maker_backend.main:app --host=0.0.0.0 --reload

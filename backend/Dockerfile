# Base stage for installing dependencies
FROM python:3.12-slim AS base

WORKDIR /tmp

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    PATH="$POETRY_HOME/bin:$PATH"

# Install python3-dev and curl
RUN apt-get update && apt-get install -y python3-dev curl

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

# Install dependencies
COPY pyproject.toml poetry.lock /tmp/
RUN poetry install --only main --no-root

# Backend image
FROM base AS backend

WORKDIR /code

COPY --from=base /tmp/.venv /project/.venv
COPY ./app /code/app
COPY ./libs /code/libs
COPY ./core /code/core
COPY ./main.py /code/main.py

ENV PATH="/project/.venv/bin:$PATH"
ENV PYTHONPATH="/project:$PYTHONPATH"

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
FROM --platform=linux/amd64 python:3.9-slim

# Set pip to have no saved cache
# No poetry venv since we run as non-root user in prod
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml /app/pyproject.toml

RUN poetry install --no-dev

COPY . /app

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]

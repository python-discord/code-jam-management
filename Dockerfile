FROM --platform=linux/amd64 python:3.9-slim as base

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_HOME="/opt/poetry" \
    INSTALL_DIR="/opt/dependencies" \
    APP_DIR="/api" \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$INSTALL_DIR/.venv/bin:$PATH"

RUN groupadd -g 61000 codejam_management \
    && useradd -g 61000 -l -r -u 61000 codejam_management

FROM base as builder
RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install --no-install-recommends -y \
  curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR $INSTALL_DIR
COPY "pyproject.toml" "poetry.lock" ./
RUN poetry install --no-dev


FROM base as development

# Create the working directory
WORKDIR $APP_DIR
COPY --from=builder $INSTALL_DIR $INSTALL_DIR

# Copy the source code in last to optimize rebuilding the image
COPY . .

USER codejam_management
# Run a single uvicorn worker
# Multiple workers are managed by kubernetes, rather than something like gunicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"]


FROM base as production
COPY --from=builder $INSTALL_DIR $INSTALL_DIR
WORKDIR $APP_DIR
COPY . .
RUN python -m compileall api/

USER codejam_management
CMD ["sh", "-c", "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000"]

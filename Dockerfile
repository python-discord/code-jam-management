FROM --platform=linux/amd64 python:3.11-slim as base

# Define Git SHA build argument for sentry
ARG git_sha="development"
ENV GIT_SHA=$git_sha

RUN groupadd -g 61000 codejam_management \
  && useradd -g 61000 -l -r -u 61000 codejam_management

# Install project dependencies
WORKDIR /app
COPY main-requirements.txt ./
RUN pip install -r main-requirements.txt

EXPOSE 8000
USER codejam_management
# Pull the uvicorn_extra build arg and ave it as an env var.
# The CMD instruction is ran at execution time, so it also needs to be an env var, so that it is available at that time.
ARG uvicorn_extras=""
ENV uvicorn_extras=$uvicorn_extras

COPY . .
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 80 $uvicorn_extras"]

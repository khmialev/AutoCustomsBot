ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

FROM base as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

FROM base

ARG PYTHON_VERSION
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION} /usr/local/lib/python${PYTHON_VERSION}
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src ./src
COPY alembic.ini ./alembic.ini
COPY --chmod=777 docker/backend/entrypoint.sh /usr/local/bin/entrypoint

ENTRYPOINT ["entrypoint"]

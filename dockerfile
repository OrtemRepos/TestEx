FROM python:3.12.6-slim-bookworm


RUN apt-get update && apt-get install -y --no-install-recommends

COPY --from=ghcr.io/astral-sh/uv:0.4.12 /uv /bin/uv

WORKDIR /app

COPY src /app/src

COPY pyproject.toml /app

COPY .env /app

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

RUN uv sync


EXPOSE 8000

ENTRYPOINT ["uv", "run", "src/main.py"]


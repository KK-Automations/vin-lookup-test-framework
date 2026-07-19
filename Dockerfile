FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/vin-lookup

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY config ./config

RUN useradd --create-home appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data
USER appuser

ENV VIN_DB_PATH=/data/vin_cache.sqlite3

EXPOSE 8000

# PORT is injected by most container hosting platforms (Render, Fly, etc.);
# it falls back to 8000 for local docker compose runs where PORT is unset.
CMD gunicorn --workers 2 --bind 0.0.0.0:${PORT:-8000} "app:create_app()"

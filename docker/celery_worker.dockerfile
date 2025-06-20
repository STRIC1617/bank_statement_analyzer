# =============================
# docker/celery_worker.dockerfile
# =============================
FROM python:3.11-slim

WORKDIR /app

COPY requirements/base.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "config.settings.celery", "worker", "--loglevel=info"]
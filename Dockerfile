# Pragma - Django OCR Invoice Processing System
# Author: Pragma Team
# Date: 2026-03-18
# Description: Docker configuration for Django application
# Multi-arch: linux/amd64, linux/arm64, linux/arm/v7

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0t64 \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py compilemessages || true
RUN python manage.py collectstatic --noinput || true

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn pragma.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"]
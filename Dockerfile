# Pragma - Django OCR Invoice Processing System
# Author: Pragma Team
# Date: 2026-03-18
# Description: Docker configuration for Django application
# Multi-arch: linux/amd64, linux/arm64, linux/arm/v7

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0t64 \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Compile translations
RUN python manage.py compilemessages || true

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run migrations and start server with gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn pragma.wsgi:application --bind 0.0.0.0:$PORT --workers 2"]
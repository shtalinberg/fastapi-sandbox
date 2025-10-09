FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements/base.pip .
COPY ./requirements/code-checks.pip .
COPY ./requirements/code-tests.pip .
COPY ./requirements/local.pip .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r local.pip

# Copy FastAPI application
COPY sc_backend/faproject/ .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
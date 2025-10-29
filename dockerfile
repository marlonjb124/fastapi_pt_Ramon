# Use official Python runtime as a parent image
FROM python:3.13-slim


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system .


COPY . .


EXPOSE 8000


CMD ["uvicorn", "main:myapp", "--host", "0.0.0.0", "--port", "8000"]

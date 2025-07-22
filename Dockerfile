FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy source code
COPY . .

# Create input/output directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV TOKENIZERS_PARALLELISM=false

# Default command
CMD ["python", "main.py"]
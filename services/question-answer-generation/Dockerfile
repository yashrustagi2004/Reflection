# ==========================================
# Question-Answer Generation Service Dockerfile
# ==========================================
# Handles AI-powered question generation using Google Gemini and Pinecone
# Port: 5003
# Python Version: 3.12.7 (Required for this service)

FROM python:3.12.7-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy shared dependencies first (for better layer caching)
COPY --chown=appuser:appuser shared/ /app/shared/

# Copy requirements files
COPY --chown=appuser:appuser question-answer-generation/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r shared/requirements.txt && \
    grep -v '^-r' requirements.txt | grep -v '^#' | grep -v '^$' | xargs -r pip install --no-cache-dir

# Copy application code
COPY --chown=appuser:appuser question-answer-generation/ .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5003/health', timeout=5)"

# Run the application
CMD ["python", "-u", "app.py"]

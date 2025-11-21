# ==========================================
# File Parsing Service Dockerfile
# ==========================================
# Handles file uploads, parsing (PDF/DOCX), and vector storage
# Port: 5002

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for file parsing
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy shared dependencies first (for better layer caching)
COPY --chown=appuser:appuser shared/ /app/shared/

# Copy requirements files
COPY --chown=appuser:appuser file-parsing/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r shared/requirements.txt && \
    grep -v '^-r' requirements.txt | grep -v '^#' | grep -v '^$' | xargs -r pip install --no-cache-dir

# Copy application code
COPY --chown=appuser:appuser file-parsing/ .

# Create uploads directory with proper permissions
RUN mkdir -p /app/uploads/resumes /app/uploads/job_descriptions && \
    chown -R appuser:appuser /app/uploads

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5002/health', timeout=5)"

# Run the application
CMD ["python", "-u", "app.py"]

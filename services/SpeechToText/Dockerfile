# ==========================================
# SpeechToText Service Dockerfile
# ==========================================
# Handles audio uploads and transcription using Google Speech Recognition
# Port: 5004
# Note: Requires FFmpeg for audio processing

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies including FFmpeg for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Create temporary directory for audio processing
RUN mkdir -p /app/temp && \
    chown -R appuser:appuser /app/temp

# Copy shared dependencies first (for better layer caching)
COPY --chown=appuser:appuser shared/ /app/shared/

# Copy requirements files
COPY --chown=appuser:appuser SpeechToText/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r shared/requirements.txt && \
    grep -v '^-r' requirements.txt | grep -v '^#' | grep -v '^$' | xargs -r pip install --no-cache-dir

# Copy application code
COPY --chown=appuser:appuser SpeechToText/ .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5004/health', timeout=5)"

# Run the application
CMD ["python", "-u", "app.py"]

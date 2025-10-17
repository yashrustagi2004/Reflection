FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for file parsing
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy shared dependencies
COPY ../shared /app/shared

# Copy service files
COPY requirements.txt .
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create uploads directory
RUN mkdir -p /app/uploads/resumes /app/uploads/job_descriptions

# Expose port
EXPOSE 5002

# Run the application
CMD ["python", "app.py"]

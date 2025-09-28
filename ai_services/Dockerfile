# ai_services/Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy only requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies (this layer will be cached unless pyproject.toml changes)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip cache purge

# Copy application code (separate layer for faster rebuilds)
COPY ai_services/src/ ./src/
COPY backend/src/app/models/ ./src/models/
COPY backend/src/utils/ ./src/utils/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8001

# Remove health check for faster startup during development
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8001/ai/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
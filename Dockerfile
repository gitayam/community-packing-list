FROM python:3.11-slim

# Set environment variables for cloud deployment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p logs media static staticfiles && \
    chown -R appuser:appuser /app

# Run migrations and collect static files
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

# Switch to non-root user
USER appuser

# Health check endpoint for Cloud Run
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1

# Cloud Run optimized Gunicorn configuration for 10k users
CMD exec gunicorn community_packing_list.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class ${WORKER_CLASS:-sync} \
    --worker-connections ${WORKER_CONNECTIONS:-2000} \
    --max-requests ${MAX_REQUESTS:-5000} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-500} \
    --timeout ${TIMEOUT:-300} \
    --keep-alive ${KEEP_ALIVE:-10} \
    --preload \
    --log-level ${LOG_LEVEL:-info} \
    --access-logfile - \
    --error-logfile - \
    --access-logformat '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %D' \
    --enable-stdio-inheritance
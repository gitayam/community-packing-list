# Multi-stage build for TypeScript compilation and Python runtime
FROM node:18-alpine AS typescript-builder

# Set work directory for TypeScript build
WORKDIR /app

# Copy package files and install Node.js dependencies (including dev dependencies for build)
COPY package*.json ./
RUN npm ci --only=production --no-audit --no-fund

# Copy TypeScript source files and configuration
COPY tsconfig.json webpack.config.js postcss.config.js .prettierrc ./
COPY src/ ./src/

# Build TypeScript files and process CSS
RUN npm run build && npm run css:build

# Python runtime stage optimized for Cloud Run
FROM python:3.12-slim AS production

# Set environment variables for Cloud Run best practices
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV PORT=8080
ENV WORKERS=1
ENV THREADS=8
ENV TIMEOUT=0

# Set work directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies with minimal packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copy entrypoint script first and set permissions
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project code into the container (exclude unnecessary files via .dockerignore)
COPY . /app/

# Copy compiled TypeScript files from builder stage
COPY --from=typescript-builder /app/packing_lists/static/packing_lists/js/ /app/packing_lists/static/packing_lists/js/
COPY --from=typescript-builder /app/packing_lists/static/packing_lists/css/compiled.css /app/packing_lists/static/packing_lists/css/

# Create directories and set proper permissions
RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1

# Switch to non-root user
USER appuser

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE $PORT

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Optimized command for Cloud Run with proper signal handling
CMD exec gunicorn community_packing_list.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance

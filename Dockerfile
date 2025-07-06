# Multi-stage build for TypeScript compilation and Python runtime
FROM node:18-alpine AS typescript-builder

# Set work directory for TypeScript build
WORKDIR /app

# Copy package files and install Node.js dependencies (including dev dependencies for build)
COPY package*.json ./
RUN npm install

# Copy TypeScript source files and configuration
COPY tsconfig.json webpack.config.js postcss.config.js .prettierrc ./
COPY src/ ./src/

# Build TypeScript files and process CSS
RUN npm run build && npm run css:build

# Python runtime stage
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script first and set permissions
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project code into the container
COPY . /app/

# Copy compiled TypeScript files from builder stage
COPY --from=typescript-builder /app/packing_lists/static/packing_lists/js/ /app/packing_lists/static/packing_lists/js/
COPY --from=typescript-builder /app/packing_lists/static/packing_lists/css/compiled.css /app/packing_lists/static/packing_lists/css/

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Expose port (Gunicorn default, or Django dev server)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - can be overridden by docker-compose.yml
CMD ["gunicorn", "community_packing_list.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--log-level", "info"]

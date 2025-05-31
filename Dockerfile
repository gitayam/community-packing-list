# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# System dependencies for psycopg2 (PostgreSQL client) and other common needs
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # Add other system dependencies if they become necessary
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin -c "Application User" appuser

# Create and set working directory
RUN mkdir /app && chown appuser:appgroup /app
WORKDIR /app

# Copy requirements file and install dependencies
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appgroup . .

# Ensure the app directory and its contents are owned by appuser
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose port 8000 for the application
EXPOSE 8000

# Default command to run the application using Gunicorn
# Note: We're now in the military_packing_list directory
WORKDIR /app/military_packing_list
CMD ["gunicorn", "military_packing_list.wsgi:application", "--bind", "0.0.0.0:8000"]

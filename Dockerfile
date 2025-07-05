# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into the container
COPY . /app/

# Expose port (Gunicorn default, or Django dev server)
EXPOSE 8000

# Add a script to be executed when the container starts
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden by docker-compose.yml)
# For development, this might be: CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# For production with Gunicorn: CMD ["gunicorn", "community_packing_list.wsgi:application", "--bind", "0.0.0.0:8000"]
# The entrypoint.sh will handle this logic.

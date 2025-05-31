# Military Packing List Pricer

## Description
The Military Packing List Pricer is a web application designed to help users track and compare prices for military gear items that might appear on official packing lists. It features a community-driven pricing model where users can submit prices from various stores. A reputation system, based on upvotes and downvotes for price submissions, helps identify reliable pricing information.

## Features
-   **Item Management**: List items, view their descriptions, and see associated prices.
-   **Price Submissions**: Users can submit prices for items, either anonymously or by providing a name.
-   **Price Viewing**: Prices are displayed sorted by cost (ascending) and then by submission date (newest first).
-   **Voting System**: Users can upvote or downvote price submissions to indicate their accuracy or helpfulness.
-   **User Reputation**: Users who submit prices under a name earn a reputation score based on the votes their submissions receive.
-   **Admin Interface**: Django admin panel for managing items, prices, and user profiles.

## Technology Stack
-   **Backend**: Python, Django
-   **Frontend**: HTML, CSS, JavaScript (for asynchronous actions like voting)
-   **Database**: PostgreSQL (configured for Docker setup)
-   **Containerization**: Docker, Docker Compose

## Prerequisites
-   Docker Engine
-   Docker Compose

## Setup and Running the Project (Using Docker)

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Environment Variables**:
    The `docker-compose.yml` file is pre-configured with default environment variables suitable for local development. These include a default `SECRET_KEY`, `DEBUG=1` (on), and database credentials.

    For **production**, these should be managed securely. This typically involves:
    -   Changing `SECRET_KEY` to a strong, unique value.
    -   Setting `DEBUG=0`.
    -   Potentially using a `.env` file (not currently implemented to be read by `docker-compose.yml` but a common pattern) or setting environment variables directly in your deployment environment.

    If you were to use a `.env` file (by modifying `docker-compose.yml` to support it or by your deployment platform), it might look like:
    ```env
    SECRET_KEY=your_super_secret_production_key_here
    DEBUG=0
    DB_NAME=packerdb
    DB_USER=packeruser
    DB_PASSWORD=supersecretprodpassword
    DB_HOST=db
    DB_PORT=5432
    ALLOWED_HOSTS_PROD=yourdomain.com,www.yourdomain.com # Comma-separated hostnames
    ```
    The `settings.py` file is configured to use `ALLOWED_HOSTS_PROD` when `DEBUG=0`.

3.  **Build and run the containers**:
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

4.  **Apply database migrations**:
    Once the containers are running, particularly the `db` service, apply database migrations:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Create a superuser**:
    To access the Django admin panel, create a superuser (this is for the PostgreSQL database inside Docker):
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email, and password.

6.  **Access the application**:
    The application should now be accessible at `http://localhost:8000`.

## Admin Access
-   Admin Panel URL: `http://localhost:8000/admin/`
-   Use the superuser credentials you created in the previous step.
    *(Note: During earlier non-Docker development with SQLite, a superuser with `admin`/`adminpassword` might have been created. That user will not exist in the new Docker PostgreSQL database unless you recreate it with the same credentials).*

## Running Tests
To run the unit tests for the `packer` app:
```bash
docker-compose exec web python manage.py test packer
```

## Stopping the Application
To stop and remove the containers (the database volume `postgres_data` will persist):
```bash
docker-compose down
```
To stop and remove containers AND the database volume (useful for a complete reset):
```bash
docker-compose down -v
```

## Further Development Notes
-   **Live Reloading**: The `web` service in `docker-compose.yml` mounts the local project directory into the container at `/app`. This means changes you make to the code (e.g., Python files, templates) should be automatically reflected by the Django development server (or Gunicorn in development mode with appropriate reload flags, though Gunicorn's primary role here is as a production-ready server). For Django's dev server, `DEBUG=True` handles this well.
-   **SECRET_KEY**: The `SECRET_KEY` set in `docker-compose.yml` or `settings.py` fallback is **for development only**. Always use a unique, secure key for production environments.
-   **Entrypoint Script**: For more automated startup (e.g., waiting for the DB to be ready before starting the web app, or running migrations automatically), an entrypoint script could be added to the `web` service in the `Dockerfile`. This has not been implemented in the current version.

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

-   Docker Engine (e.g., version 20.10 or later)
-   Docker Compose (e.g., version 1.29 or later, or Docker Compose V2 included with newer Docker Desktop versions)

## Installation and Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd military-packing-list-pricer # Or your project's directory name
    ```

2.  **Configure Environment Variables**:
    -   This project uses an `.env` file to manage environment-specific settings such as secret keys, database credentials, and port mappings. Docker Compose automatically loads this file if it exists in the project root.
    -   Copy the provided template to create your own environment file:
        ```bash
        cp .env-template .env
        ```
    -   Open the `.env` file in a text editor and customize the variables:
        -   **`SECRET_KEY`**: **Critical!** Change this to a unique, long, and random string. The default value is insecure and for development only.
        -   **`DB_PASSWORD`**: Set a strong password for the database user (`packeruser`). The default is `supersecretpackerpassword`.
        -   **`DEBUG`**: Set to `1` for development (enables detailed error pages and auto-reloading). Set to `0` for production.
        -   **`ALLOWED_HOSTS_PROD`**: If `DEBUG=0`, this **must** be set to the domain(s) your site will be hosted on (e.g., `yourdomain.com,www.yourdomain.com`). For development with `DEBUG=1`, this is less critical as `settings.py` has more permissive defaults.
        -   **`WEB_APP_HOST_PORT`**: (Optional) The port on your host machine that will map to the application's port 8000 inside the container. Defaults to `8000`.
        -   **`DB_HOST_PORT`**: (Optional) The port on your host machine that will map to the PostgreSQL database port 5432 inside the container. Defaults to `5432`. This is useful if you need to connect to the database directly from your host machine using a DB client.
        -   Other variables like `DB_NAME` (`packerdb`), `DB_USER` (`packeruser`), `DB_HOST` (`db` - which is the service name for PostgreSQL in Docker Compose), `DB_PORT` (`5432` - container internal port) can usually be left as their defaults for local Docker development.

3.  **Build and Run with Docker Compose**:
    -   This command will build the Docker images (if they don't exist or if the `Dockerfile`/code has changed) and start the application (`web`) and database (`db`) services in detached mode (`-d`).
        ```bash
        docker-compose up --build -d
        ```

4.  **Apply Database Migrations**:
    -   Once the containers are running (especially the `db` service), apply the database migrations to set up the necessary tables:
        ```bash
        docker-compose exec web python manage.py migrate
        ```

5.  **Create a Superuser (Admin Account)**:
    -   Create an administrator account to access the Django admin interface. This user will be stored in the PostgreSQL database.
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
    -   Follow the prompts to set a username, email, and password.

6.  **Access the Application**:
    -   The web application should now be running. You can access it in your browser at `http://localhost:${WEB_APP_HOST_PORT}` (e.g., `http://localhost:8000` if you used the default port specified in `.env-template` or `docker-compose.yml`).
    -   The Django admin panel is available at `http://localhost:${WEB_APP_HOST_PORT}/admin/`.

## Admin Access
-   Admin Panel URL: `http://localhost:${WEB_APP_HOST_PORT}/admin/` (e.g. `http://localhost:8000/admin/`)
-   Use the superuser credentials you created during **Step 5** of the "Installation and Setup" process.

## Running Tests

To run the unit tests for the `packer` app:
```bash
docker-compose exec web python manage.py test packer
```

## Stopping the Application

-   To stop the services (web and db):
    ```bash
    docker-compose down
    ```
-   To stop the services AND remove the data volumes (e.g., to completely reset the database):
    ```bash
    docker-compose down -v
    ```

## Further Development Notes
-   **Live Reloading**: The `web` service in `docker-compose.yml` mounts the local project directory (`.`) into the container at `/app`. When `DEBUG=1`, Django's development server (run by Gunicorn in this setup, but Gunicorn passes through to Django's WSGI app) will automatically reload Python code changes. Template changes are also typically picked up.
-   **SECRET_KEY Security**: The `SECRET_KEY` in `.env-template` and the fallback in `docker-compose.yml` are placeholders. **Always** use a unique, cryptographically strong secret key for any production or sensitive environment. Do not commit your actual production `.env` file with the real secret key to version control.
-   **Entrypoint Script**: For more complex startup sequences (e.g., waiting for the database to be fully ready before the web application starts, or automatically running migrations on startup), an entrypoint script can be added to the `web` service's Docker image. This has not been implemented in the current version for simplicity.

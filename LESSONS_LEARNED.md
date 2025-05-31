# Lessons Learned - Military Packing List Pricer

This document captures key lessons learned during the development of the Military Packing List Pricer application. These insights are intended to help streamline future development and troubleshooting for projects involving Django, Docker, PostgreSQL, and related technologies.

## Table of Contents
1. [Django Development](#django-development)
    - [Models and ORM](#models-and-orm)
    - [Views and Templates](#views-and-templates)
    - [Forms](#forms)
    - [Static Files and Media](#static-files-and-media)
    - [Settings and Configuration](#settings-and-configuration)
    - [Migrations](#migrations)
2. [Docker and Docker Compose](#docker-and-docker-compose)
    - [Dockerfile Best Practices](#dockerfile-best-practices)
    - [Docker Compose for Multi-Container Apps](#docker-compose-for-multi-container-apps)
    - [Environment Variables](#environment-variables)
    - [Networking](#networking)
    - [Volumes and Data Persistence](#volumes-and-data-persistence)
3. [PostgreSQL Integration](#postgresql-integration)
    - [Database Setup in Docker](#database-setup-in-docker)
    - [Django Integration with `psycopg2`](#django-integration-with-psycopg2)
    - [Data Integrity and Backups](#data-integrity-and-backups)
4. [Gunicorn (WSGI Server)](#gunicorn-wsgi-server)
    - [Configuration and Usage in Docker](#configuration-and-usage-in-docker)
    - [Performance Considerations](#performance-considerations)
5. [Frontend (HTML/CSS/JavaScript)](#frontend-htmlcssjavascript)
    - [Django Template Language](#django-template-language)
    - [Basic JavaScript for Interactivity](#basic-javascript-for-interactivity)
    - [CSS Styling](#css-styling)
6. [Development Workflow and Testing](#development-workflow-and-testing)
    - [Environment Setup (.env files)](#environment-setup-env-files)
    - [Running the Application Locally](#running-the-application-locally)
    - [Admin Interface Usage](#admin-interface-usage)
    - [Unit Testing with Django](#unit-testing-with-django)
    - [Debugging Strategies](#debugging-strategies)

---

## 1. Django Development

### Models and ORM
-   **✅ What Worked Well:**
    -   Django's ORM simplified database interactions significantly. Defining models in Python is intuitive.
    -   Relationships (ForeignKey) were straightforward to implement for `Price` to `Item`.
    -   `auto_now_add=True` for `submitted_at` fields is convenient.
    -   Using `DecimalField` for `price` ensures precision for currency.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Remembering to run `makemigrations` and `migrate` after model changes. Forgetting can lead to schema mismatches.
    -   Deciding between `on_delete=models.CASCADE` vs. other options (`SET_NULL`, `PROTECT`) requires careful thought about data integrity. `CASCADE` was appropriate here for prices when an item is deleted.
    -   For more complex apps, `UserProfile` might typically be linked via a ForeignKey from `Price` rather than relying on matching `submitted_by_name` if full user accounts were a primary feature from the start. This project's approach was a simplification for anonymous/name-based submissions.
-   **🔧 Standard Operating Procedure:**
    -   Always run `makemigrations <app_name>` and `migrate` after any change to `models.py`.
    -   Use `DecimalField` for monetary values.
    -   Plan relationships and `on_delete` behavior carefully.
    -   For user-submitted content, consider how to link to user profiles as the app scales.

### Views and Templates
-   **✅ What Worked Well:**
    -   Function-based views were sufficient for this project's complexity.
    -   Django's template language (`DTL`) is powerful for rendering dynamic data. `{% url %}` tag is essential for maintainable URLs.
    -   Using `get_object_or_404` simplifies error handling for non-existent objects.
    -   Separation of concerns: views handle logic, templates handle presentation.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Over-stuffing views with logic that could belong in model methods or helper functions.
    -   DTL can be limiting for complex frontend logic; knowing when to use JavaScript is key.
    -   Forgetting `{% csrf_token %}` in POST forms leads to 403 errors.
-   **🔧 Standard Operating Procedure:**
    -   Keep views concise. Offload complex data logic to models or managers if appropriate.
    -   Use template inheritance (`{% extends %}`, `{% block %}`) extensively to keep templates DRY.
    -   Always include `{% csrf_token %}` in forms that modify data.
    -   Use `reverse` or `reverse_lazy` in views and `{% url %}` in templates for URL generation.

### Forms
-   **✅ What Worked Well:**
    -   `ModelForm` simplifies form creation directly from models (`PriceForm`).
    -   Django handles form validation well (e.g., ensuring price is a decimal).
    -   `form.is_valid()` and `form.cleaned_data` provide a clear workflow for processing form data.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Customizing widget rendering or adding specific CSS classes sometimes requires more effort (e.g., using `django-widget-tweaks` or manually rendering fields).
    -   Ensuring that `save(commit=False)` is used when needing to modify the instance before final save (e.g., assigning the `item` to a `Price`).
-   **🔧 Standard Operating Procedure:**
    -   Use `ModelForm` when forms map directly to models.
    -   Handle `commit=False` correctly when additional data needs to be set on the model instance before saving.
    -   Leverage Django's built-in validators and add custom validation as needed.

### Static Files and Media
-   **✅ What Worked Well:**
    -   Django's static file handling (`{% load static %}`, `STATIC_URL`) is straightforward for CSS, JS, and images.
    -   Organizing static files per app (`app_name/static/app_name/`) is a good convention.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Forgetting to run `collectstatic` in a production-like environment (though not strictly an issue with Docker dev server if configured correctly).
    -   Understanding the difference between `STATIC_URL`, `STATIC_ROOT`, and `STATICFILES_DIRS`.
-   **🔧 Standard Operating Procedure:**
    -   Use `{% static %}` template tag for all static file URLs.
    -   Organize static files within each app's `static` directory.
    -   Ensure `django.contrib.staticfiles` is in `INSTALLED_APPS`.

### Settings and Configuration
-   **✅ What Worked Well:**
    -   Centralized configuration in `settings.py`.
    -   Using environment variables (via `os.environ.get()`) for sensitive data like `SECRET_KEY` and database credentials, making the app adaptable to Docker.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Hardcoding secrets or environment-specific paths directly in `settings.py`.
    -   Managing `ALLOWED_HOSTS` correctly for development vs. production.
    -   Ensuring `DEBUG` is `False` in production.
-   **🔧 Standard Operating Procedure:**
    -   Store all secrets and environment-specific configurations in environment variables (e.g., loaded from an `.env` file in development).
    -   Set `DEBUG=False` in production.
    -   Configure `ALLOWED_HOSTS` carefully for production environments.
    -   Keep `INSTALLED_APPS`, `MIDDLEWARE` well-organized.

### Migrations
-   **✅ What Worked Well:**
    -   Django's migration system is robust for evolving database schema.
    -   `makemigrations` and `migrate` commands are clear.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Migration conflicts if multiple developers work on the same models simultaneously without coordination (not an issue for this solo project).
    -   Reversing migrations can sometimes be tricky, especially if data transformations are involved.
    -   It's generally bad practice to edit migration files manually unless you know exactly what you're doing.
-   **🔧 Standard Operating Procedure:**
    -   Always generate migrations with `makemigrations` after model changes.
    -   Apply migrations with `migrate`.
    -   Commit migration files to version control.
    -   Test migrations in a staging environment before applying to production.

---

## 2. Docker and Docker Compose

### Dockerfile Best Practices
-   **✅ What Worked Well:**
    -   Using a slim Python base image (`python:3.9-slim`) keeps the image size down.
    -   Creating a non-root user (`appuser`) for running the application enhances security.
    -   Setting `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1` is good practice for Python apps in Docker.
    -   Copying `requirements.txt` and installing dependencies before copying the rest of the application code leverages Docker's layer caching.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Forgetting to include necessary system dependencies (e.g., `libpq-dev gcc` for `psycopg2`) can cause `pip install` to fail.
    -   Large build contexts if `.dockerignore` is not used effectively (not a major issue for this small project).
    -   Ensuring correct file ownership and permissions for the non-root user.
-   **🔧 Standard Operating Procedure:**
    -   Start with an official slim base image.
    -   Run the application as a non-root user.
    -   Optimize layer caching by ordering commands correctly (e.g., install dependencies before copying application code).
    -   Use a `.dockerignore` file to exclude unnecessary files/directories from the build context.
    -   Install system dependencies explicitly.

### Docker Compose for Multi-Container Apps
-   **✅ What Worked Well:**
    -   `docker-compose.yml` makes it easy to define and manage multi-service applications (web, db).
    -   `depends_on` controls startup order.
    -   Named volumes for database persistence (`postgres_data`) are crucial.
    -   Mapping ports for host access is straightforward.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Understanding Docker networking (default bridge network vs. custom networks). For this project, the default network created by Compose is sufficient.
    -   Managing environment variables securely and effectively across services.
    -   Forgetting to rebuild images (`docker-compose up --build`) after Dockerfile changes.
-   **🔧 Standard Operating Procedure:**
    -   Define services clearly with explicit build contexts/images, ports, volumes, and environment variables.
    -   Use named volumes for persistent data.
    -   Leverage `.env` files for environment-specific configuration.
    -   Use `docker-compose up --build` to ensure image changes are applied.

### Environment Variables
-   **✅ What Worked Well:**
    -   Using an `.env-template` and `.env` file provides a clear way to manage configuration.
    -   Docker Compose automatically loads variables from an `.env` file in the project root.
    -   Parameterizing `docker-compose.yml` (e.g., `${SECRET_KEY:-default_value}`) offers flexibility.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Committing `.env` files containing secrets to version control (always add `.env` to `.gitignore`).
    -   Ensuring type consistency (e.g., `DEBUG=1` vs `DEBUG='1'` and how it's parsed in Python).
    -   Precedence of environment variables (e.g., shell-exported vs. `.env` vs. `environment` block in Compose).
-   **🔧 Standard Operating Procedure:**
    -   Add `.env` to `.gitignore`.
    -   Provide a `.env-template` or similar example file.
    -   Load sensitive configurations like `SECRET_KEY`, database passwords, and API keys from environment variables.
    -   Ensure Django's `settings.py` correctly parses these variables (e.g., `DEBUG = os.environ.get('DEBUG') == '1'`).

### Networking
-   **✅ What Worked Well:**
    -   Docker Compose automatically sets up a network, allowing services (`web`, `db`) to communicate using service names as hostnames (e.g., `DB_HOST=db`).
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Debugging network connectivity issues between containers.
    -   Exposing container ports unnecessarily to the host machine.
-   **🔧 Standard Operating Procedure:**
    -   Rely on Docker Compose service names for inter-container communication.
    -   Only expose ports on the host if external access is needed (e.g., web app port, or DB port for debugging).

### Volumes and Data Persistence
-   **✅ What Worked Well:**
    -   Named volumes (e.g., `postgres_data`) ensure database data persists across container restarts and removals.
    -   Bind mounts (`.:/app`) are excellent for development, allowing live code reloading.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Understanding the difference between named volumes and bind mounts.
    -   Permissions issues with bind mounts if host user and container user UIDs/GIDs don't align (less of an issue when running as a dedicated `appuser` created within Dockerfile).
-   **🔧 Standard Operating Procedure:**
    -   Use named volumes for data that needs to persist (e.g., databases).
    -   Use bind mounts for code during development to see changes live.
    -   Be mindful of what data is stored in volumes vs. what should be part of the image.

---

## 3. PostgreSQL Integration

### Database Setup in Docker
-   **✅ What Worked Well:**
    -   Using the official `postgres:13-alpine` image is convenient and provides a lightweight database server.
    -   Setting `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` environment variables in `docker-compose.yml` automatically initializes the database.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Ensuring the database service is fully up and ready before the web application tries to connect (though `depends_on` helps, a wait script is more robust for production).
    -   Managing database schema migrations in a Dockerized environment.
-   **🔧 Standard Operating Procedure:**
    -   Use official PostgreSQL images.
    -   Configure database credentials and name via environment variables.
    -   Use a named volume for data persistence.
    -   Run Django migrations (`docker-compose exec web python manage.py migrate`) after the DB container is up.

### Django Integration with `psycopg2`
-   **✅ What Worked Well:**
    -   `psycopg2-binary` is easy to install via `requirements.txt`.
    -   Configuring Django's `DATABASES` setting using environment variables for host, port, name, user, password works reliably.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Missing system dependencies (`libpq-dev`, `gcc`) for `psycopg2` (not `psycopg2-binary`) can cause installation issues. `psycopg2-binary` avoids this for most common cases.
-   **🔧 Standard Operating Procedure:**
    -   Include `psycopg2-binary` in `requirements.txt`.
    -   Configure `settings.DATABASES` to use environment variables passed from `docker-compose.yml`.

### Data Integrity and Backups
-   **✅ What Worked Well:**
    -   PostgreSQL is a robust RDBMS that ensures data integrity.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   This project does not implement automated backups. In a production scenario, regular backups of the PostgreSQL volume are critical.
-   **🔧 Standard Operating Procedure:**
    -   For production, implement a backup strategy for the PostgreSQL data volume (e.g., using `pg_dump` and cron jobs, or cloud provider backup solutions).

---

## 4. Gunicorn (WSGI Server)

### Configuration and Usage in Docker
-   **✅ What Worked Well:**
    -   Using Gunicorn as the WSGI server for the Django application in Docker is standard practice.
    -   Simple command in Dockerfile/`docker-compose.yml`: `gunicorn military_packing_list.wsgi:application --bind 0.0.0.0:8000`.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Tuning Gunicorn worker count and type for optimal performance (not deeply explored in this project).
    -   Serving static files efficiently (Gunicorn is not ideal for this; typically use Nginx or Whitenoise in front/alongside Gunicorn in production). This project relies on Django's dev static file serving due to `DEBUG=True`.
-   **🔧 Standard Operating Procedure:**
    -   Use Gunicorn to serve the Django WSGI application.
    -   Bind to `0.0.0.0` to make it accessible from outside the container.
    -   For production, configure appropriate worker settings and consider a reverse proxy like Nginx for serving static files and SSL termination.

### Performance Considerations
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Default Gunicorn settings (e.g., a single synchronous worker) may not be optimal for handling concurrent requests in a production environment, potentially leading to performance bottlenecks.
    -   Not configuring aspects like worker timeouts or keep-alive settings can affect reliability under load.
-   **🔧 Standard Operating Procedure:**
    -   For production, research and configure Gunicorn worker settings appropriately. A common starting point is `workers = (2 * CPU_CORES) + 1`.
    -   Choose the appropriate worker type (sync, async like gevent/uvicorn) based on application I/O profile and Django's async capabilities (if used). This project used default sync workers.
    -   Monitor application performance under load and adjust Gunicorn settings as needed.
    -   Consider parameters like `--worker-connections`, `--timeout`, and `--keep-alive`.
    -   (Note: Detailed Gunicorn performance tuning was outside the immediate scope of this project's initial setup, which used basic Gunicorn defaults suitable for development and demonstration.)

---

## 5. Frontend (HTML/CSS/JavaScript)

### Django Template Language
-   **✅ What Worked Well:**
    -   DTL is sufficient for rendering dynamic content and basic logic within templates.
    -   Template inheritance (`{% extends %}`, `{% block %}`) and inclusion (`{% include %}`) help create reusable components.
    -   Filters like `|date` and `|floatformat` are useful.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Limited capabilities compared to modern JavaScript frameworks.
    -   Can become cluttered if too much logic is embedded directly.
-   **🔧 Standard Operating Procedure:**
    -   Use DTL for presentation logic.
    -   Keep complex logic in views or JavaScript.
    -   Utilize template inheritance and includes.

### Basic JavaScript for Interactivity
-   **✅ What Worked Well:**
    -   Vanilla JavaScript was used effectively for the asynchronous voting feature (`fetch` API).
    -   Accessing CSRF token from the DOM for AJAX POST requests is a common pattern.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Constructing URLs for `fetch` requests (using `{% url %}` in a script tag or data attributes helps).
    -   Managing JavaScript code as it grows (for larger apps, consider a bundler or more structured approach).
    -   Ensuring the CSRF token is correctly included in `POST` requests made via `fetch`.
-   **🔧 Standard Operating Procedure:**
    -   Use `fetch` API for modern asynchronous requests.
    -   Pass CSRF token in request headers (`X-CSRFToken`).
    -   Organize JavaScript code logically, potentially in separate static files.

### CSS Styling
-   **✅ What Worked Well:**
    -   Basic CSS in a single `style.css` file was enough for this project's UI needs.
    -   Using classes to style elements provides good separation.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   CSS can become hard to manage for larger projects (consider methodologies like BEM, or preprocessors like SASS/LESS, or utility-first CSS).
    -   Cross-browser compatibility (though less of an issue with modern browsers for basic CSS).
-   **🔧 Standard Operating Procedure:**
    -   Organize CSS with clear, reusable classes.
    -   For larger projects, adopt a CSS methodology or framework.

---

## 6. Development Workflow and Testing

### Environment Setup (.env files)
-   **✅ What Worked Well:**
    -   Using `.env-template` and `.env` files makes setup consistent and keeps secrets out of version control.
    -   Docker Compose automatically picking up `.env` is convenient.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   User forgetting to copy `.env-template` to `.env` or fill in required variables.
-   **🔧 Standard Operating Procedure:**
    -   Provide a clear `.env-template`.
    -   Document which variables are essential to change in the README.
    -   Add `.env` to `.gitignore`.

### Running the Application Locally
-   **✅ What Worked Well:**
    -   `docker-compose up --build -d` provides a single command to get the entire stack running.
    -   Volume mounting for live code changes speeds up development.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Initial setup time if Docker images need to be downloaded/built.
    -   Ensuring correct ports are mapped and not conflicting with other local services.
-   **🔧 Standard Operating Procedure:**
    -   Use `docker-compose up` for starting services.
    -   Use `docker-compose down` (and `docker-compose down -v` to remove volumes) for stopping.

### Admin Interface Usage
-   **✅ What Worked Well:**
    -   Django's built-in admin interface is excellent for managing data without writing custom views, especially during development and for admin tasks.
    -   Registering models with `admin.py` is simple. Customizing `list_display`, `readonly_fields` etc. is useful.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   The admin interface can become slow if not optimized for models with very large numbers of records or complex relationships (not an issue here).
-   **🔧 Standard Operating Procedure:**
    -   Register all important models with the admin site.
    -   Customize admin views (`ModelAdmin`) for better usability.
    -   Secure the admin interface properly in production.

### Unit Testing with Django
-   **✅ What Worked Well:**
    -   Django's `TestCase` class provides a good framework for writing tests, including a test client and automatic database setup/teardown.
    -   `reverse()` is useful for generating URLs in tests.
    -   Testing models, views, and forms separately helps isolate issues.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Writing meaningful tests that cover edge cases, not just "happy path".
    -   Mocking external services or complex dependencies if they were part of the project.
    -   Ensuring tests are independent and don't rely on state from previous tests.
-   **🔧 Standard Operating Procedure:**
    -   Write tests for all critical application logic.
    -   Aim for high test coverage.
    -   Run tests regularly during development and before commits/deployments.
    -   Use `self.client` for testing views.

### Debugging Strategies
-   **✅ What Worked Well:**
    -   Django's debug page (when `DEBUG=True`) is very informative for exceptions.
    -   `print()` statements or `logging` module for quick debugging in views/logic.
    -   `docker-compose logs <service_name>` for viewing container logs.
    -   Using the Django shell (`docker-compose exec web python manage.py shell`) to inspect data or test ORM queries.
-   **⚠️ Potential Pitfalls / Challenges:**
    -   Debugging issues within Docker containers can sometimes be trickier than local native development if not familiar with Docker exec/logs.
    -   JavaScript debugging requires browser developer tools.
-   **🔧 Standard Operating Procedure:**
    -   Utilize Django's debug page in development.
    -   Use `docker-compose logs -f web` to tail logs.
    -   Use the Django shell for data inspection.
    -   For more complex debugging, consider tools like `pdb` or IDE debuggers that can attach to Docker containers.

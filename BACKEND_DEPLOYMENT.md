# Backend Deployment Guide

This guide covers deploying the Django REST API backend for the Community Packing List application.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Development with Docker](#local-development-with-docker)
- [Deployment Options](#deployment-options)
  - [Option 1: Render (Recommended)](#option-1-render-recommended)
  - [Option 2: Railway](#option-2-railway)
  - [Option 3: Google Cloud Run](#option-3-google-cloud-run)
  - [Option 4: Heroku](#option-4-heroku)
- [Environment Variables](#environment-variables)
- [Post-Deployment Steps](#post-deployment-steps)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Overview

The backend is a Django 5.2.4 application with:
- **Framework**: Django REST Framework 3.15.1
- **Database**: PostgreSQL 16 (production) / SQLite3 (development)
- **Web Server**: Gunicorn 22.0.0
- **Static Files**: WhiteNoise 6.6.0
- **CORS**: django-cors-headers 4.3.1

**Tech Stack Summary**:
```
Django 5.2.4
├── Django REST Framework 3.15.1
├── PostgreSQL driver (psycopg2-binary 2.9.10)
├── Gunicorn 22.0.0
├── WhiteNoise 6.6.0
├── django-cors-headers 4.3.1
└── File parsers (pandas, openpyxl, PyPDF2, pdfplumber)
```

---

## Prerequisites

- Python 3.13+ installed
- PostgreSQL 16+ (for production deployment)
- Docker and Docker Compose (for local testing)
- Git configured with repository access
- Account on chosen deployment platform

---

## Local Development with Docker

### Quick Start with Docker Compose

1. **Clone the repository**:
```bash
git clone https://github.com/gitayam/community-packing-list.git
cd community-packing-list
```

2. **Start services**:
```bash
docker-compose up -d
```

This will:
- Start PostgreSQL 16 on port 5432
- Start Django on port 8000
- Run migrations automatically
- Create sample data
- Enable hot-reload for development

3. **Access the API**:
- API Root: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- Health Check: http://localhost:8000/api/health/

4. **View logs**:
```bash
docker-compose logs -f web
```

5. **Stop services**:
```bash
docker-compose down
```

### Local Development without Docker

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Copy environment file**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run migrations**:
```bash
python3 manage.py migrate
```

5. **Create sample data** (optional):
```bash
python3 manage.py create_example_data
```

6. **Run development server**:
```bash
python3 manage.py runserver
```

---

## Deployment Options

### Option 1: Render (Recommended)

**Why Render?**
- ✅ Free tier with PostgreSQL database
- ✅ Automatic deployments from Git
- ✅ Built-in SSL certificates
- ✅ Easy environment variable management
- ✅ Zero-configuration PostgreSQL

**Deployment Steps**:

1. **Push code to GitHub**:
```bash
git add .
git commit -m "feat: Add backend deployment configuration"
git push origin main
```

2. **Create Render Account**:
- Go to https://render.com
- Sign up with GitHub account

3. **Deploy using Blueprint** (Automated):

   The repository includes `render.yaml` for automated deployment:

   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select branch: `main`
   - Render will automatically:
     - Create PostgreSQL database
     - Create web service
     - Set up environment variables
     - Deploy the application

4. **Manual Setup** (Alternative):

   **a. Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `community-packing-list-db`
   - Database Name: `community_packing_list`
   - User: `cpl_user`
   - Region: Oregon (or closest to your users)
   - Plan: Free
   - Click "Create Database"

   **b. Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `community-packing-list-api`
   - Region: Oregon (same as database)
   - Branch: `main`
   - Runtime: Python 3
   - Build Command:
     ```bash
     pip install -r requirements.txt && python3 manage.py collectstatic --noinput
     ```
   - Start Command:
     ```bash
     gunicorn community_packing_list.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 60
     ```
   - Plan: Free

   **c. Configure Environment Variables**:

   In the web service settings, add:
   ```
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<generate-random-secret-key>
   DJANGO_ALLOWED_HOSTS=.onrender.com
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=<from-database-internal-database-name>
   DB_USER=<from-database-username>
   DB_PASS=<from-database-password>
   DB_HOST=<from-database-hostname>
   DB_PORT=<from-database-port>
   CSRF_TRUSTED_ORIGINS=https://community-packing-list.pages.dev https://*.community-packing-list.pages.dev
   PYTHON_VERSION=3.13.7
   ```

5. **Run Initial Setup**:

   In the Render Shell:
   ```bash
   python3 manage.py migrate
   python3 manage.py createsuperuser
   python3 manage.py create_example_data
   ```

6. **Get API URL**:
   - Your API will be at: `https://community-packing-list-api.onrender.com`
   - Health check: `https://community-packing-list-api.onrender.com/api/health/`

---

### Option 2: Railway

**Why Railway?**
- ✅ Modern developer experience
- ✅ Automatic HTTPS
- ✅ PostgreSQL plugin
- ✅ Simple pricing

**Deployment Steps**:

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Login to Railway**:
```bash
railway login
```

3. **Create New Project**:
```bash
railway init
```

4. **Add PostgreSQL**:
```bash
railway add postgresql
```

5. **Set Environment Variables**:
```bash
railway variables set DJANGO_DEBUG=False
railway variables set DJANGO_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
railway variables set CSRF_TRUSTED_ORIGINS="https://community-packing-list.pages.dev https://*.community-packing-list.pages.dev"
```

6. **Deploy**:
```bash
railway up
```

7. **Run Migrations**:
```bash
railway run python3 manage.py migrate
railway run python3 manage.py createsuperuser
railway run python3 manage.py create_example_data
```

8. **Get Domain**:
```bash
railway domain
```

---

### Option 3: Google Cloud Run

**Why Cloud Run?**
- ✅ Serverless - pay per use
- ✅ Auto-scaling
- ✅ Google Cloud ecosystem integration

**Deployment Steps**:

1. **Install gcloud CLI**:
```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
```

2. **Initialize gcloud**:
```bash
gcloud init
gcloud auth login
```

3. **Create Project**:
```bash
gcloud projects create community-packing-list --name="Community Packing List"
gcloud config set project community-packing-list
```

4. **Enable APIs**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

5. **Create Cloud SQL Instance**:
```bash
gcloud sql instances create cpl-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-west1

gcloud sql databases create community_packing_list --instance=cpl-db
gcloud sql users create cpl_user --instance=cpl-db --password=<secure-password>
```

6. **Build and Deploy**:
```bash
gcloud builds submit --tag gcr.io/community-packing-list/api

gcloud run deploy community-packing-list-api \
  --image gcr.io/community-packing-list/api \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars DJANGO_DEBUG=False \
  --set-env-vars DJANGO_ALLOWED_HOSTS=.run.app \
  --add-cloudsql-instances community-packing-list:us-west1:cpl-db
```

7. **Configure Environment Variables**:
```bash
gcloud run services update community-packing-list-api \
  --update-env-vars DB_ENGINE=django.db.backends.postgresql \
  --update-env-vars DB_NAME=community_packing_list \
  --update-env-vars DB_USER=cpl_user \
  --update-env-vars DB_HOST=/cloudsql/community-packing-list:us-west1:cpl-db
```

---

### Option 4: Heroku

**Why Heroku?**
- ✅ Mature platform
- ✅ Extensive documentation
- ✅ Add-on marketplace

**Deployment Steps**:

1. **Install Heroku CLI**:
```bash
brew install heroku/brew/heroku  # macOS
# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login**:
```bash
heroku login
```

3. **Create App**:
```bash
heroku create community-packing-list-api
```

4. **Add PostgreSQL**:
```bash
heroku addons:create heroku-postgresql:essential-0
```

5. **Set Environment Variables**:
```bash
heroku config:set DJANGO_DEBUG=False
heroku config:set DJANGO_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
heroku config:set CSRF_TRUSTED_ORIGINS="https://community-packing-list.pages.dev https://*.community-packing-list.pages.dev"
```

6. **Deploy**:
```bash
git push heroku main
```

7. **Run Migrations**:
```bash
heroku run python3 manage.py migrate
heroku run python3 manage.py createsuperuser
heroku run python3 manage.py create_example_data
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_DEBUG` | Debug mode (False in production) | `False` |
| `DJANGO_SECRET_KEY` | Secret key for Django | Generate with: `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hostnames | `.onrender.com` or `.run.app` |
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `community_packing_list` |
| `DB_USER` | Database user | `cpl_user` |
| `DB_PASS` | Database password | `<secure-password>` |
| `DB_HOST` | Database hostname | From your database provider |
| `DB_PORT` | Database port | `5432` |
| `CSRF_TRUSTED_ORIGINS` | CORS origins | `https://community-packing-list.pages.dev` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHON_VERSION` | Python version | `3.13.7` |
| `PORT` | Server port | `8000` |

### Generating Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Post-Deployment Steps

### 1. Run Migrations

```bash
# Render Shell or Railway CLI
python3 manage.py migrate
```

### 2. Create Superuser

```bash
python3 manage.py createsuperuser
```

### 3. Load Sample Data

```bash
python3 manage.py create_example_data
```

### 4. Test API Endpoints

```bash
# Health check
curl https://your-api-url.com/api/health/

# Get packing lists
curl https://your-api-url.com/api/packing-lists/

# Get stores
curl https://your-api-url.com/api/stores/
```

### 5. Update Frontend Environment Variable

In Cloudflare Pages dashboard:
1. Go to Settings → Environment Variables
2. Update `VITE_API_URL` to your deployed API URL
3. Redeploy frontend

---

## Monitoring and Maintenance

### Health Check

The API includes a health check endpoint:
```
GET /api/health/
```

Response:
```json
{
  "status": "healthy",
  "service": "community-packing-list-api"
}
```

### Logs

**Render**:
```bash
# View in dashboard or CLI
render logs -s community-packing-list-api
```

**Railway**:
```bash
railway logs
```

**Google Cloud Run**:
```bash
gcloud run services logs read community-packing-list-api
```

**Heroku**:
```bash
heroku logs --tail
```

### Database Backups

**Render**: Automatic daily backups on paid plans

**Railway**: Automatic backups

**Google Cloud SQL**:
```bash
gcloud sql backups create --instance=cpl-db
```

**Heroku**:
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Scaling

**Render**: Upgrade plan in dashboard

**Railway**: Automatic scaling based on load

**Cloud Run**: Automatic, configure max instances:
```bash
gcloud run services update community-packing-list-api --max-instances=10
```

**Heroku**:
```bash
heroku ps:scale web=2
```

---

## Troubleshooting

### Common Issues

**Issue**: Static files not loading
```bash
# Run collectstatic
python3 manage.py collectstatic --noinput --clear
```

**Issue**: Database connection errors
- Verify all `DB_*` environment variables
- Check database host allows connections
- Verify database credentials

**Issue**: CORS errors
- Update `CSRF_TRUSTED_ORIGINS` in environment variables
- Ensure Cloudflare Pages domain is included
- Check `CORS_ALLOWED_ORIGINS` in settings.py

**Issue**: 500 Internal Server Error
- Check logs for error details
- Verify `DJANGO_SECRET_KEY` is set
- Ensure `DEBUG=False` in production
- Run migrations: `python3 manage.py migrate`

### Debug Mode

**Never enable DEBUG in production!**

For debugging, check logs:
```bash
# Render
render logs -s community-packing-list-api --tail

# Railway
railway logs

# Cloud Run
gcloud run services logs read community-packing-list-api --limit=50

# Heroku
heroku logs --tail --app community-packing-list-api
```

---

## Next Steps

1. ✅ Deploy backend to chosen platform
2. ✅ Run migrations and create sample data
3. ✅ Test all API endpoints
4. ✅ Update frontend `VITE_API_URL`
5. ✅ Redeploy frontend on Cloudflare Pages
6. ✅ Test end-to-end integration
7. ✅ Set up monitoring and alerts
8. ✅ Configure database backups
9. ✅ Document API URL in DEPLOYMENT_STATUS.md

---

## Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Heroku Python Documentation](https://devcenter.heroku.com/categories/python-support)

---

**Last Updated**: January 2025
**Backend Version**: v3.0.0
**Django Version**: 5.2.4

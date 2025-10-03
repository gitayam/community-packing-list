# Deployment Guide - Community Packing List

Complete guide for deploying the React + Django stack to production.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│   Cloudflare Pages (React Frontend) │
│   - React 19 + Vite                 │
│   - Edge deployment                 │
│   - https://community-packing-list  │
│         .pages.dev                   │
└──────────────┬──────────────────────┘
               │ API calls
               │ /api/*
               ▼
┌─────────────────────────────────────┐
│   Django Backend (REST API)         │
│   - Django 5.2.4 + DRF              │
│   - PostgreSQL/SQLite               │
│   - Railway/Render/Fly.io           │
└─────────────────────────────────────┘
```

## 🚀 Frontend Deployment (Cloudflare Pages)

### Prerequisites
- Cloudflare account
- Wrangler CLI installed (`npm install -D wrangler`)
- Git repository

### Option 1: Automatic (GitHub Integration)

1. **Connect Repository**
   ```bash
   # Push to GitHub
   git push origin cloudflare/react-migration
   ```

2. **Setup Cloudflare Pages**
   - Go to https://dash.cloudflare.com/
   - Pages → Create a project
   - Connect to GitHub
   - Select repository: `community-packing-list`
   - Configure build settings:
     - **Build command:** `cd frontend-react && npm run build`
     - **Build output:** `frontend-react/dist`
     - **Root directory:** `/` (or `frontend-react`)

3. **Environment Variables**
   ```
   VITE_API_URL = https://your-backend.com/api
   ```

4. **Deploy**
   - Automatic on every push to main branch
   - Preview deployments for PRs

### Option 2: Manual (Wrangler CLI)

```bash
# Navigate to React app
cd frontend-react

# Login to Cloudflare
npx wrangler login

# Create Pages project (first time only)
npx wrangler pages project create community-packing-list \
  --production-branch=main

# Build and deploy
npm run build
npx wrangler pages deploy dist \
  --project-name=community-packing-list \
  --commit-dirty=true

# Or use the npm script
npm run wrangler:deploy
```

### Custom Domain

1. Go to Pages project → Custom domains
2. Add domain: `packing.yourdomain.com`
3. Follow DNS instructions
4. Enable "Always Use HTTPS"

## 🐳 Backend Deployment (Django)

### Option A: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL
railway add postgresql

# Deploy
railway up
```

**Environment Variables:**
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.railway.app
DB_ENGINE=django.db.backends.postgresql
DATABASE_URL=postgresql://... (auto-set by Railway)
```

### Option B: Render

1. **Create Web Service**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repository
   - Configure:
     - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command:** `gunicorn community_packing_list.wsgi:application`
     - **Python Version:** 3.12

2. **Add PostgreSQL Database**
   - Dashboard → New → PostgreSQL
   - Copy DATABASE_URL

3. **Environment Variables**
   ```env
   DJANGO_SECRET_KEY=<generate-strong-key>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-app.onrender.com
   DATABASE_URL=postgres://...
   ```

### Option C: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy
```

Create `fly.toml`:
```toml
app = "community-packing-list"
primary_region = "iad"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

## 🗄️ Database Setup

### PostgreSQL (Production)

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create sample data
python manage.py create_example_data
```

### Database Backup

```bash
# Backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## 🔐 Security Checklist

### Django Backend

- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup HTTPS (Let's Encrypt)
- [ ] Enable CORS for React frontend only
- [ ] Use environment variables for secrets
- [ ] Setup database backups
- [ ] Configure logging
- [ ] Enable CSRF protection
- [ ] Secure session cookies

### React Frontend

- [ ] Remove console.logs in production
- [ ] Set correct `VITE_API_URL`
- [ ] Enable CSP headers
- [ ] Configure caching headers
- [ ] Minify and optimize assets

## 🔄 CI/CD Pipeline

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install and Build
        run: |
          cd frontend-react
          npm ci
          npm run build
      - name: Deploy to Cloudflare
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: 'frontend-react'
          command: pages deploy dist --project-name=community-packing-list

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 📊 Monitoring & Logging

### Frontend (Cloudflare)

- **Analytics:** Cloudflare Pages dashboard
- **Real-time logs:** `wrangler pages deployment tail`
- **Error tracking:** Sentry (optional)

### Backend (Django)

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 🧪 Testing Deployments

### Frontend

```bash
# Test production build locally
npm run build
npm run preview

# Visit http://localhost:4173
```

### Backend

```bash
# Test with production settings
export DJANGO_DEBUG=False
python manage.py runserver

# Run checks
python manage.py check --deploy
```

### End-to-End

1. Deploy backend first
2. Note the backend URL
3. Update frontend `VITE_API_URL`
4. Deploy frontend
5. Test all features:
   - [ ] Create packing list
   - [ ] Upload file
   - [ ] Add items
   - [ ] Toggle packed status
   - [ ] Add price
   - [ ] Vote on price
   - [ ] Manage stores

## 🚨 Rollback Procedure

### Frontend (Cloudflare)

```bash
# View deployments
npx wrangler pages deployment list \
  --project-name=community-packing-list

# Rollback to previous deployment
# (Use Cloudflare dashboard or redeploy specific commit)
git checkout <previous-commit>
npm run wrangler:deploy
```

### Backend (Railway/Render)

- Dashboard → Deployments → Rollback to previous

## 📈 Performance Optimization

### Frontend

- ✅ Code splitting (automatic with Vite)
- ✅ Lazy loading routes
- ✅ Image optimization
- ✅ Gzip compression (Cloudflare)
- ✅ CDN caching (Cloudflare Edge)

### Backend

- [ ] Enable Django caching
- [ ] Database query optimization
- [ ] Add database indexes
- [ ] Enable gzip middleware
- [ ] Setup Redis for sessions (optional)

## 🔗 Production URLs

After deployment, update these URLs:

- **Frontend:** `https://community-packing-list.pages.dev`
- **Backend:** `https://your-backend.railway.app/api`
- **Admin:** `https://your-backend.railway.app/admin`

## 📞 Support

For deployment issues:
- Cloudflare: https://community.cloudflare.com/
- Railway: https://discord.gg/railway
- Render: https://render.com/docs
- Django: https://docs.djangoproject.com/

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed to Cloudflare Pages
- [ ] Backend deployed with PostgreSQL
- [ ] Environment variables configured
- [ ] Database migrated
- [ ] Sample data created
- [ ] CORS configured correctly
- [ ] HTTPS enabled
- [ ] Custom domain (optional)
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] All features tested
- [ ] Performance optimized
- [ ] Security hardened

**🎉 Your app is now live!**

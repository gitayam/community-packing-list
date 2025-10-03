# Community Packing List

A modern full-stack web application for creating, sharing, and managing structured packing lists for military schools, training courses, and deployments.

[![Production Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/gitayam/community-packing-list)
[![React Version](https://img.shields.io/badge/react-19-61dafb.svg)](https://react.dev/)
[![Django Version](https://img.shields.io/badge/django-5.2-blue.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🏗️ Architecture

**Frontend**: React 19 + TypeScript + Vite → Deployed on Cloudflare Pages
**Backend**: Django 5.2 + Django REST Framework → PostgreSQL

**Live Demo**: https://community-packing-list.pages.dev

## 🚀 Features

### Core Functionality
- **Structured Packing Lists**: Create organized lists with sections, categories, and detailed item information
- **Item Management**: Add, edit, and organize items with quantities, NSN/LIN codes, required/optional flags
- **School and Base Association**: Link packing lists to specific schools and military bases
- **Price Tracking**: Community-driven price information with voting system
- **Store Locator**: Find stores near schools/bases or your current location

### Advanced Features  
- **Public Sharing**: Share lists with unique URLs and embed widgets
- **File Import**: Upload CSV, Excel, or PDF files to create packing lists
- **Text Parsing**: Paste text content to quickly create lists
- **Modal Interfaces**: Modern popup forms for adding prices and items
- **Compact Table Display**: Optimized table layout with expandable price details

### Modern UI/UX
- **Responsive Design**: Mobile-first approach with modern CSS
- **Interactive Elements**: Smooth animations and hover effects
- **Compact Pricing**: Shows best value with expandable additional prices
- **Enhanced Item Display**: Bold item names and organized information
- **Accessibility**: ARIA labels, keyboard navigation, and focus management

## 🛠️ Tech Stack

### Frontend
- **React 19** - Latest React with modern patterns
- **TypeScript 5.9** - Type safety and developer experience
- **Vite 7** - Lightning-fast build tool
- **TanStack Query 5** - Server state management
- **React Router 7** - Client-side routing
- **React Hook Form + Zod** - Form handling and validation
- **Tailwind CSS 4** - Utility-first styling
- **Cloudflare Pages** - Edge deployment

### Backend
- **Django 5.2** - Python web framework
- **Django REST Framework 3.15** - RESTful API
- **PostgreSQL** - Relational database
- **django-cors-headers** - CORS middleware
- **Gunicorn** - Production WSGI server

## 🛠️ Quick Start

### React Frontend (Development)

```bash
# Clone the repository
git clone https://github.com/gitayam/community-packing-list.git
cd community-packing-list/frontend-react

# Install dependencies
npm install

# Start dev server
npm run dev

# Visit http://localhost:5173
```

### Django Backend (Development)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create sample data
python manage.py create_example_data

# Start Django server
python manage.py runserver

# API available at http://localhost:8000/api
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## 📁 Project Structure

```
community-packing-list/
├── frontend-react/              # React 19 frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Route components
│   │   ├── hooks/              # React Query hooks
│   │   ├── lib/                # API client, schemas, utils
│   │   └── types/              # TypeScript definitions
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
├── community_packing_list/     # Django project configuration
│   └── settings.py            # DRF + CORS configuration
├── packing_lists/             # Django REST API
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── api_views.py           # API ViewSets
│   ├── api_urls.py            # API routing
│   ├── views.py               # Django template views (legacy)
│   └── migrations/            # Database migrations
├── deployment/                # Deployment scripts
├── requirements.txt           # Python dependencies (includes DRF)
├── manage.py                  # Django management commands
├── API.md                     # REST API documentation
├── DEPLOYMENT.md              # Deployment guide
├── ROADMAP.md                 # Feature roadmap
└── README.md                  # This file
```

## 🚀 Deployment Options

### Frontend Deployment (Cloudflare Pages)

**Automatic (GitHub Integration):**
```bash
# Push to GitHub
git push origin main

# Cloudflare Pages auto-deploys
# Build command: cd frontend-react && npm run build
# Build output: frontend-react/dist
```

**Manual (Wrangler CLI):**
```bash
cd frontend-react
npx wrangler login
npm run build
npx wrangler pages deploy dist --project-name=community-packing-list
```

**Live URL**: https://community-packing-list.pages.dev

### Backend Deployment (Django REST API)

**Option 1: Railway**
```bash
railway login
railway init
railway add postgresql
railway up
```

**Option 2: Render**
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command: `gunicorn community_packing_list.wsgi:application`

**Option 3: Google Cloud Run**
```bash
gcloud auth login
./deployment/deploy-cloud.sh
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🔧 Configuration

### Frontend Environment Variables

Create `frontend-react/.env.local`:

```bash
VITE_API_URL=http://localhost:8000/api  # Development
# VITE_API_URL=https://your-backend.railway.app/api  # Production
```

### Backend Environment Variables

Create a `.env` file at the root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packing_list_db

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# CORS (for React frontend)
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://community-packing-list.pages.dev
```

### Database Setup

The application uses PostgreSQL with automatic migrations:

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load example data (optional)
python manage.py loaddata example_data.json
```

## 📊 Features Overview

### Modal Functionality
- ✅ Add Price modals open as popups (not new pages)
- ✅ Add Item modals with AJAX form submission
- ✅ Proper event handling and form validation

### Table Display Optimization
- ✅ Compact pricing display with expandable details
- ✅ Removed Notes and Instructions columns for cleaner layout
- ✅ Bold item names for better readability
- ✅ Responsive row heights

### Sharing Features
- ✅ Public list sharing with unique URLs
- ✅ Embeddable widgets for external sites
- ✅ Social media integration
- ✅ Community discovery page

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test packing_lists.tests.test_models
python manage.py test packing_lists.tests.test_views

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Performance

The application is optimized for production:

- **Database**: Query optimization with select_related and prefetch_related
- **Static Files**: WhiteNoise for static file serving
- **Caching**: Redis caching for frequently accessed data
- **Images**: Optimized image serving with proper compression
- **CSS/JS**: Minified assets for faster loading

## 🔒 Security

Production security features:

- **HTTPS**: Enforced in production
- **CSRF Protection**: Django's built-in CSRF middleware
- **SQL Injection**: Protection via Django ORM
- **XSS Protection**: Template auto-escaping
- **Secure Headers**: Security middleware configuration

## 🌟 Recent Improvements

### React Migration (v3.0.0 - October 2025)
- **Complete frontend rewrite** in React 19 with TypeScript
- **Modern React patterns**: Suspense, ErrorBoundary, skeleton loading
- **TanStack Query**: Optimized server state management with caching
- **Cloudflare Pages**: Edge deployment for global performance
- **Django REST API**: Full REST API with Django REST Framework
- **Type safety**: Complete TypeScript coverage
- **Modern build tools**: Vite 7 for lightning-fast builds
- **Tailwind CSS 4**: Preserved military theme with utility-first CSS

### Modal and UX Enhancements (v2.1.0)
- Fixed modal functionality for Add Price/Add Item buttons
- Implemented compact pricing display with expandable details
- Removed redundant table columns for cleaner layout
- Enhanced item name prominence and readability
- Improved responsive design for mobile devices

### Sharing Platform (v2.0.0)
- Public list sharing with unique URLs
- Embeddable widgets for external websites
- Social media integration (Twitter, Facebook, Reddit)
- Community discovery page with search and filtering
- SEO optimization with meta tags and structured data

## 📚 Documentation

- **[API Documentation](API.md)** - Complete REST API reference
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[React Frontend README](frontend-react/README.md)** - React app documentation
- [Feature Roadmap](ROADMAP.md)
- [Legacy Development Docs](docs/) - Django template version docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

See [ROADMAP.md](ROADMAP.md) for upcoming features and improvements.

---

**Production Ready**: This application is battle-tested and ready for production deployment with comprehensive error handling, monitoring, and scalability features.
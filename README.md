# Community Packing List

A production-ready Django web application for creating, sharing, and managing structured packing lists for military schools, training courses, and deployments.

[![Production Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/gitayam/community-packing-list)
[![Django Version](https://img.shields.io/badge/django-4.2-blue.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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

## 🛠️ Quick Start

### Production Deployment (Google Cloud Run)

```bash
# Clone the repository
git clone https://github.com/gitayam/community-packing-list.git
cd community-packing-list

# Deploy to Google Cloud Run
./deployment/deploy-cloud.sh
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/gitayam/community-packing-list.git
cd community-packing-list

# Start local development environment
./deployment/deploy-local.sh

# Access the application
open http://localhost:8000
```

## 📁 Project Structure

```
community-packing-list/
├── community_packing_list/     # Django project configuration
├── packing_lists/             # Main Django application
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JavaScript, images
│   └── migrations/           # Database migrations
├── deployment/               # Deployment scripts and configurations
│   ├── deploy-cloud.sh       # Google Cloud Run deployment
│   └── deploy-local.sh       # Local development setup
├── docs/                     # Documentation
│   ├── LessonsLearned.md     # Development lessons
│   ├── SCALING_ROADMAP.md    # Scaling plans
│   └── LOCAL_DEVELOPMENT.md  # Local development guide
├── Dockerfile               # Production container configuration
├── docker-compose.yml       # Local development containers
├── docker-compose.cloud.yml # Cloud deployment containers
├── requirements.txt         # Python dependencies
├── manage.py               # Django management commands
├── ROADMAP.md              # Feature roadmap
└── README.md               # This file
```

## 🚀 Deployment Options

### 1. Google Cloud Run (Recommended for Production)

The application is optimized for Google Cloud Run deployment:

```bash
# Set up Google Cloud authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy to Cloud Run
./deployment/deploy-cloud.sh
```

**Features:**
- Auto-scaling based on traffic
- HTTPS by default
- PostgreSQL Cloud SQL integration
- Static file serving via Cloud Storage
- Health checks and monitoring

### 2. Local Development

For local development with Docker:

```bash
# Start all services
./deployment/deploy-local.sh

# Or manually with Docker Compose
docker-compose up -d

# Create admin user
python manage.py createsuperuser
```

**Services included:**
- Django application (port 8000)
- PostgreSQL database
- Redis (for caching)
- Static file serving

### 3. Docker Production

For self-hosted production deployment:

```bash
# Build production image
docker build -t community-packing-list .

# Run with docker-compose
docker-compose -f docker-compose.cloud.yml up -d
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packing_list_db

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Cloud Storage (optional)
GCS_BUCKET_NAME=your-bucket-name
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

- [Deployment Guide](docs/LOCAL_DEVELOPMENT.md)
- [Scaling Roadmap](docs/SCALING_ROADMAP.md)
- [Development Lessons](docs/LessonsLearned.md)
- [Feature Roadmap](ROADMAP.md)

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
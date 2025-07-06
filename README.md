# Community Packing List

A Django-based web application for creating, sharing, and managing structured packing lists for military schools, training courses, and deployments.

## 🚀 Features

### Core Functionality
- **Structured Packing Lists**: Create organized packing lists with sections, categories, and detailed item information
- **Item Management**: Add, edit, and organize items with quantities, NSN/LIN codes, required/optional flags, and special instructions
- **School and Base Association**: Link packing lists to specific schools and military bases
- **Price Tracking**: Community-driven price information with voting system
- **Store Locator**: Find stores near schools/bases or your current location

### Advanced Features
- **File Import**: Upload CSV, Excel, or PDF files to create packing lists
- **Text Parsing**: Paste text content to quickly create lists
- **Structured Display**: Items organized by sections with clear visual indicators
- **Packing Status**: Check off items as you pack them
- **Inline Store Creation**: Add new stores while adding prices

### Modern Frontend Technology
- **TypeScript**: Modern type-safe JavaScript with strict configuration
- **Webpack**: Module bundling with code splitting and optimization
- **PostCSS**: Advanced CSS processing with autoprefixer and optimization
- **ESLint & Prettier**: Code quality and consistency enforcement
- **Responsive Design**: Mobile-first approach with modern CSS Grid and Flexbox
- **Component Architecture**: Reusable UI components with TypeScript
- **Performance Optimized**: Lazy loading, intersection observers, and efficient animations

### Example Data
The application includes a comprehensive Ranger School packing list example with:
- 35+ items organized into 7 categories
- Realistic NSN/LIN codes
- Required vs optional item flags
- Detailed instructions and notes
- Associated school (Ranger School) and base (Fort Benning)

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- Python 3.8+ (for local development)
- Node.js 18+ (for local development)

### Environment Setup

- **Do NOT commit your `.env` file to version control.**
- Use `.env.example` as the template for environment variables. Copy it to `.env` for local development only:

```bash
cp .env.example .env
# Edit .env with your local or deployment-specific settings
```

- For production and CI, set environment variables securely using your deployment platform or secrets manager.

### Production Setup with Docker

```bash
# Clone the repository
git clone <repository-url>
cd community-packing-list

# Set up environment
cp .env.example .env
# Edit .env with your database settings

# Build and run in production mode
docker-compose --profile prod up --build
```

### Development Setup with Docker

```bash
# Clone the repository
git clone <repository-url>
cd community-packing-list

# Set up environment
cp .env.example .env
# Edit .env with your database settings

# Development with hot reloading
docker-compose --profile dev up --build

# Or use the dedicated development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Local Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build frontend assets
npm run build
npm run css:build

# Set up database
python manage.py migrate
python manage.py create_example_data

# Start development servers
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: TypeScript watch mode
npm run dev

# Terminal 3: CSS watch mode
npm run css:dev
```

## 🔧 Development

### Frontend Development

The application uses a modern TypeScript-based frontend architecture:

```bash
# Install dependencies
npm install

# Development mode with watch (TypeScript)
npm run dev

# Development mode with watch (CSS)
npm run css:dev

# Build for production
npm run build
npm run css:build

# Type checking
npm run type-check

# Linting and formatting
npm run lint
npm run lint:fix
npm run format

# Testing
npm test

# Clean build artifacts
npm run clean
```

### Backend Development

```bash
# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations
python manage.py migrate

# Create example data
python manage.py create_example_data

# Clear all data (development only)
python manage.py flush

# Collect static files
python manage.py collectstatic
```

### Docker Development Commands

```bash
# Production build
docker-compose --profile prod up --build

# Development with hot reloading
docker-compose --profile dev up --build

# Build only TypeScript assets
docker-compose run --rm typescript-dev npm run build

# Run tests in container
docker-compose run --rm web python manage.py test

# Access Django shell
docker-compose run --rm web python manage.py shell

# Create superuser
docker-compose run --rm web python manage.py createsuperuser
```

## 📁 Project Structure

```
community-packing-list/
├── src/                          # TypeScript source files
│   ├── components/               # Reusable UI components
│   │   └── Modal.ts             # Modal component
│   ├── styles/                   # CSS source files
│   │   └── main.css             # Main stylesheet
│   ├── utils/                    # Utility functions
│   │   └── index.ts             # Advanced TypeScript utilities
│   ├── types.ts                  # TypeScript type definitions
│   ├── common.ts                 # Common utilities and API client
│   ├── packing-list-detail.ts    # Packing list detail page
│   ├── store-list.ts             # Store list page
│   ├── packing-list-form.ts      # Packing list form
│   └── price-form-modal.ts       # Price form modal
├── packing_lists/                # Django app
│   ├── static/packing_lists/     # Static files
│   │   ├── css/                  # Compiled CSS
│   │   └── js/                   # Compiled JavaScript
│   ├── templates/                # Django templates
│   └── ...                       # Django app files
├── docker-compose.yml            # Production Docker setup
├── docker-compose.dev.yml        # Development Docker setup
├── Dockerfile                    # Multi-stage Docker build
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript configuration
├── webpack.config.js             # Webpack bundling
├── postcss.config.js             # PostCSS configuration
└── .prettierrc                   # Code formatting rules
```

## 🎨 Design System

The application uses a modern design system with:

- **CSS Custom Properties**: Consistent design tokens for colors, spacing, typography
- **Component-Based Architecture**: Reusable UI components
- **Mobile-First Design**: Responsive layouts that work on all devices
- **Accessibility**: ARIA attributes, focus management, keyboard navigation
- **Performance**: Optimized animations and lazy loading

## 📱 Usage

### Creating Packing Lists
1. **Manual Creation**: Use the "Create New Packing List" form
2. **File Upload**: Upload CSV, Excel, or PDF files
3. **Text Import**: Paste text content for quick list creation

### Managing Items
- **Add Items**: Use the "Add New Item" button on any packing list
- **Edit Items**: Click "Edit" on any item row
- **Structured Fields**: Include sections, NSN/LIN codes, required flags, and instructions

### Price Information
- **Add Prices**: Click "Add Price" for any item
- **Vote on Prices**: Upvote/downvote community-submitted prices
- **Store Information**: Find stores near your location or school/base

## 🗃️ Data Models

### PackingList
- Name, description, type (Course, Selection, Training, Deployment, Other)
- Associated school and/or base
- Custom type for "Other" category

### PackingListItem
- Section/category organization
- NSN/LIN codes
- Required vs optional flags
- Special instructions and notes
- Packing status tracking

### School/Base
- Location information with coordinates
- Address details for proximity calculations

### Store
- Complete address information
- GPS coordinates for distance calculations
- Price information for items

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure TypeScript builds successfully
6. Run linting and formatting
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

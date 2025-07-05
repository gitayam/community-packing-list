# Community Packing List

A Django-based web application for creating, sharing, and managing structured packing lists for military schools, training courses, and deployments.

## Features

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

### Frontend Technology
- **TypeScript**: Modern type-safe JavaScript for better development experience
- **Webpack**: Module bundling and asset optimization
- **ESLint**: Code quality and consistency enforcement
- **Responsive Design**: Mobile-first approach with modern CSS

### Example Data
The application includes a comprehensive Ranger School packing list example with:
- 35+ items organized into 7 categories
- Realistic NSN/LIN codes
- Required vs optional item flags
- Detailed instructions and notes
- Associated school (Ranger School) and base (Fort Benning)

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Docker and Docker Compose (recommended)

### Installation with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd community-packing-list
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. Build and run with Docker:
   ```bash
   docker-compose up --build
   ```
   
   This will:
   - Build the TypeScript frontend assets
   - Set up the PostgreSQL database
   - Run database migrations
   - Create example data
   - Start the development server

### Alternative Manual Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies (for TypeScript compilation):
   ```bash
   npm install
   ```

3. Build TypeScript assets:
   ```bash
   npm run build
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

5. Run the startup script:
   ```bash
   python3 startup.py
   ```

## Development

### TypeScript Development

The frontend uses TypeScript for better type safety and developer experience:

```bash
# Install dependencies
npm install

# Development mode with watch
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix
```

### Running Tests
```bash
python3 manage.py test
```

### Creating Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Management Commands
```bash
# Create example data
python3 manage.py create_example_data

# Clear all data (development only)
python3 manage.py flush
```

## Usage

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

## Data Models

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure TypeScript builds successfully
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

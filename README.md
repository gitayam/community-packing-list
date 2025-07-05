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

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd community-packing-list
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

4. Run the startup script (recommended):
   ```bash
   python3 startup.py
   ```
   This will:
   - Run database migrations
   - Create example data
   - Start the development server

### Alternative Manual Setup
```bash
# Run migrations
python3 manage.py migrate

# Create example data
python3 manage.py create_example_data

# Start server
python3 manage.py runserver
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

## Development

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

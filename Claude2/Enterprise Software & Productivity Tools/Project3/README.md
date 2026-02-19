# Intelligent Document Classification and Retrieval System

A production-ready full-stack application for automated document management, featuring AI-powered classification, intelligent search, analytics, and reporting.

## Features

### 🎯 Core Features
- **Document Upload & Storage**: Upload PDF, DOCX, and TXT files up to 50MB
- **Automatic Text Extraction**: Extract text content from all supported file formats
- **AI-Powered Classification**: Automatic categorization using Naive Bayes/SVM classifiers
- **Intelligent Search**: TF-IDF based semantic search with relevance ranking
- **Real-time Analytics**: Track searches, views, and access patterns
- **Visual Reports**: Interactive charts and graphs using Chart.js

### 📊 Dashboard
- Document statistics and counts
- Category distribution charts
- Recent uploads tracking
- Most viewed documents
- Quick search functionality

### 🔍 Search Capabilities
- Full-text search across document content
- Category and file type filters
- Relevance scoring
- Similar document recommendations

### 📈 Analytics & Reports
- Search trends over time
- Top search queries
- Access pattern analysis
- Most accessed documents
- Upload and view trends
- Category and type distributions

## Tech Stack

### Backend
- **Python 3.13+**
- **Django 6.0** - Web framework
- **Django REST Framework** - API endpoints
- **SQLite** - Database (default)

### AI/ML
- **scikit-learn** - Machine learning (Naive Bayes, SVM)
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **NLTK** - Natural language processing

### Text Processing
- **PyPDF2/pypdf** - PDF text extraction
- **python-docx** - Word document extraction
- **TF-IDF Vectorization** - Search indexing

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **Vanilla JavaScript (ES6+)** - No framework dependencies
- **Chart.js 4.4** - Data visualization

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\Dell\OneDrive\Desktop\Claude2\Enterprise Software & Productivity Tools\Project3"
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Frontend: http://127.0.0.1:8000/
   - API Endpoints: http://127.0.0.1:8000/api/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage

### Uploading Documents

1. Navigate to the **Upload** page
2. Fill in the document title (required)
3. Select a file (PDF, DOCX, or TXT)
4. Optionally add a description
5. Optionally select a category (or let AI auto-classify)
6. Click **Upload Document**

The system will:
- Extract text from the document
- Automatically classify it into a category
- Make it searchable immediately

### Searching Documents

1. Use the **Search** page or quick search in header
2. Enter search keywords
3. Optionally filter by category or file type
4. View results ranked by relevance

### Viewing Analytics

1. Visit the **Analytics** page
2. Select time period (7, 30, or 90 days)
3. View search trends, top queries, and access patterns

### Generating Reports

1. Go to the **Reports** page
2. View interactive charts showing:
   - Category distribution
   - File type distribution
   - Upload trends
   - View trends

## Project Structure

```
Project3/
├── docsystem/              # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI config
├── documents/             # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views & handlers
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin interface
│   ├── text_extraction.py # Text extraction logic
│   ├── classifier.py      # ML classifier
│   └── search.py          # Search engine
├── templates/             # Frontend templates
│   ├── index.html         # Main SPA
│   └── static/
│       ├── css/style.css  # Styles
│       └── js/app.js      # Frontend logic
├── media/                 # Uploaded documents
├── static/                # Static files
├── db.sqlite3            # SQLite database
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Categories
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Documents
- `GET /api/documents/` - List documents (with filtering, sorting, pagination)
- `POST /api/documents/upload/` - Upload new document
- `GET /api/documents/{id}/` - Get document details
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document
- `POST /api/documents/{id}/reclassify/` - Re-classify with AI
- `POST /api/documents/{id}/track_view/` - Track document view
- `GET /api/documents/{id}/similar/` - Find similar documents

### Search
- `GET /api/search/?query=keyword&category=Finance&file_type=pdf&limit=20` - Search documents

### Dashboard
- `GET /api/dashboard/` - Get dashboard statistics

### Analytics
- `GET /api/analytics/?days=30` - Get analytics data

### Reports
- `GET /api/reports/` - Get reporting data for charts

## ML Classification

The system uses **Naive Bayes** and **SVM** classifiers with **TF-IDF** vectorization:

### Default Categories
- **Finance** - Budgets, financial reports, invoices, taxes
- **HR** - Employee, recruitment, policies, benefits
- **Legal** - Contracts, agreements, compliance, regulations
- **Technical** - Software, development, specifications, documentation
- **General** - Reports, memos, announcements

The classifier is pre-trained with synthetic data and works out-of-the-box. It can be retrained with custom data.

## Configuration

### Settings (docsystem/settings.py)

```python
# File upload
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Allowed file size (in DocumentUploadSerializer)
max_size = 50 * 1024 * 1024  # 50MB

# Pagination
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating New Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Admin Panel
Access at `/admin/` to manage:
- Categories
- Documents
- Search queries
- Access logs
- System stats

## Troubleshooting

### NLTK Data Download
If you see NLTK errors, the system will automatically download required data on first run.

### File Upload Issues
- Check file size (max 50MB)
- Verify file format (PDF, DOCX, TXT only)
- Ensure media directory has write permissions

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
```

## Production Deployment

For production deployment:

1. **Set DEBUG=False in settings.py**
2. **Configure ALLOWED_HOSTS**
3. **Set up a production database (PostgreSQL recommended)**
4. **Configure static files serving**
5. **Use a production WSGI server (Gunicorn)**
6. **Set up a reverse proxy (Nginx)**
7. **Configure environment variables for sensitive data**

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check:
- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- scikit-learn: https://scikit-learn.org/

---

**Built with ❤️ using Django, scikit-learn, and vanilla JavaScript**

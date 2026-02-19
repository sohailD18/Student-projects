# AI-Driven Smart Shopping Assistant 🛒🤖

A complete e-commerce shopping assistant built with Django that provides intelligent product recommendations, comparisons, and conversational AI support.

## Features

### Core Functionality
- **Conversational AI Interface**: Chat-based shopping assistant with Mock AI (easily replaceable with OpenAI/Anthropic)
- **Product Search & Filter**: Advanced search with category, price range, and rating filters
- **Comparison Engine**: Side-by-side product comparison with AI-generated summaries
- **Recommendation System**: Personalized recommendations based on user preferences
- **Decision Support**: Visual badges (Best Value, Top Rated, Premium) on products

### Technical Stack
- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Mock AI Service (structured for easy API integration)

## Project Structure

```
smart_shopper/
├── assistant/                    # Main Django app
│   ├── models.py                # Database models
│   ├── views.py                 # All API endpoints
│   ├── urls.py                  # URL routing
│   ├── admin.py                 # Django admin configuration
│   ├── management/              # Management commands
│   │   └── commands/
│   │       └── populate_products.py  # Populate sample products
│   └── templates/assistant/     # HTML templates
│       ├── base.html           # Base layout
│       └── index.html          # Main dashboard
├── smart_shopper/               # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── venv/                        # Virtual environment
├── manage.py                    # Django management script
└── db.sqlite3                   # SQLite database (created after migration)
```

## Database Models

### Product
- UUID, name, description, price, category
- Image URL, specs (JSON), rating
- Indexed on category, price, and rating

### UserPreference
- User ID, preferred categories (JSON)
- Budget range (JSON), style tags (JSON)

### InteractionHistory
- User ID, query text, interaction type
- Many-to-many relationship with Products

### ChatSession & ChatMessage
- Session tracking with timestamps
- Message history with role (user/assistant)

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Navigate to Project Directory
```bash
cd Project5
```

### Step 2: Virtual Environment Setup
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# OR (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install django
```

### Step 4: Database Migration
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for Admin Panel)
```bash
python manage.py createsuperuser
```
Follow prompts to create username, email, and password.

### Step 6: Populate Sample Products
```bash
python manage.py populate_products
```

This will populate the database with 20 sample electronic products:
- Laptops (5 products)
- Phones (5 products)
- Headphones (6 products)
- Budget options (4 products)

### Step 7: Run Development Server
```bash
python manage.py runserver
```

### Step 8: Access the Application

**Main Application**: http://127.0.0.1:8000/

**Admin Panel**: http://127.0.0.1:8000/admin/

## API Endpoints

### Frontend Views
- `GET /` - Main dashboard

### API Endpoints

#### Search & Filter
- `GET /api/search/?q=query&category=Laptop&min_price=0&max_price=1000`
- Returns: List of matching products with badges

#### Compare Products
- `POST /api/compare/`
- Body: `{"product_ids": ["id1", "id2", ...]}`
- Returns: Side-by-side comparison with AI summary

#### Get Recommendations
- `GET /api/recommendations/?user_id=123&category=Laptop&limit=6`
- Returns: Personalized product recommendations

#### Chat Interface
- `POST /api/chat/`
- Body: `{"message": "Show me laptops under $1000", "session_id": "optional"}`
- Returns: AI response with optional product recommendations

#### Chat History
- `GET /api/chat/history/?session_id=uuid`
- Returns: Complete chat history for a session

#### Update Preferences
- `POST /api/preferences/`
- Body: `{"user_id": "123", "categories": ["Laptop"], "budget_range": {"min": 0, "max": 1000}}`
- Returns: Updated user preferences

## Using the Application

### 1. Chat with AI Assistant
Type natural language queries in the chat interface:
- "Show me laptops under $1000"
- "What are the best headphones?"
- "Compare iPhone vs Samsung"
- "Recommend a phone under $500"

### 2. Quick Actions
Use the quick action buttons for common queries:
- Laptops under $1500
- Best Headphones
- Phone Deals
- Compare Products

### 3. Product Grid
- Browse products by category using the dropdown filter
- Click "Compare" on product cards to add them to comparison
- View badges for Top Rated, Best Value, and Premium products

### 4. Compare Products
- Add 2-4 products to comparison
- Click "Compare Selected" to see detailed comparison
- View AI-generated comparison summary
- See side-by-side specifications table

## Mock AI Service

The application uses a rule-based Mock AI Service that can be easily replaced with OpenAI or Anthropic API.

### Current Mock AI Patterns
Located in `assistant/views.py:355-525`

The Mock AI handles:
- Greeting detection (hi, hello, hey)
- Product search with price constraints
- Category-based product listing
- Comparison requests
- Recommendation requests
- Specifications inquiries

### Replacing with Real AI

To integrate OpenAI API:

```python
# In assistant/views.py, replace _mock_ai_process() with:

import openai

openai.api_key = 'your-api-key-here'

def _real_ai_process(message, session):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful shopping assistant..."},
            {"role": "user", "content": message}
        ]
    )

    ai_response_text = response.choices[0].message.content

    # Call search/filter functions based on AI response
    # ... logic to extract products and format response ...

    return {
        'text': ai_response_text,
        'type': 'ai_response',
        'products': relevant_products
    }
```

Similarly for Anthropic Claude:

```python
import anthropic

client = anthropic.Anthropic(api_key='your-api-key')

def _real_ai_process(message, session):
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": message}]
    )

    # Process response and format
    return formatted_response
```

## Admin Panel

Access at: http://127.0.0.1:8000/admin/

### Features
- Manage Products (CRUD operations)
- View User Preferences
- Monitor Chat Sessions
- Review Interaction History
- Filter and search all data

## Customization

### Adding New Products
Use the admin panel or run:
```bash
python manage.py shell
```
```python
from assistant.models import Product
Product.objects.create(
    name="New Product",
    description="Description here",
    price=999.99,
    category="Laptop",
    specs={"processor": "Intel i7", "ram": "16GB"},
    rating=4.5
)
```

### Modifying Categories
Edit the populate_products command or add through admin panel.

### Styling
Modify CSS in:
- `assistant/templates/assistant/base.html` (global styles)
- `assistant/templates/assistant/index.html` (page-specific styles)

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
```bash
# Delete database and re-migrate
rm db.sqlite3
python manage.py migrate
python manage.py populate_products
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Development Notes

### Security Considerations
- CSRF exempt on chat endpoint for ease of use (enable in production)
- No authentication required (add if needed)
- Secret key in settings (change for production)

### Performance Optimization
- Product search limited to 20 results
- Products indexed on category, price, rating
- Chat session persistence in localStorage

### Future Enhancements
- Real OpenAI/Anthropic integration
- User authentication
- Order tracking
- Payment integration
- Product reviews
- Wishlist functionality

## Support

For issues or questions:
1. Check Django documentation: https://docs.djangoproject.com/
2. Review code comments in views.py and models.py
3. Check browser console for JavaScript errors
4. Check Django debug output for server errors

## License

This is a project for educational purposes. Feel free to modify and extend.

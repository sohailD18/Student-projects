# Quick Start Guide - Smart Shopping Assistant

## 5-Minute Setup

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies (Already Done!)
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python manage.py runserver
```

### 4. Open in Browser
**Main App**: http://127.0.0.1:8000/

**Admin Panel**: http://127.0.0.1:8000/admin/

---

## Demo Commands to Try

Once the app is running, try these commands in the chat:

1. **Budget Search**: `Show me laptops under $1000`
2. **Category Browse**: `What are the best headphones?`
3. **Comparison**: `Compare MacBook and Dell XPS`
4. **Recommendation**: `Recommend a phone under $800`
5. **Specs Query**: `What are the specs of iPhone 15 Pro?`

---

## Project Files Overview

### Backend (Python/Django)
- **[assistant/models.py](assistant/models.py)** - 5 database models (Product, UserPreference, ChatSession, etc.)
- **[assistant/views.py](assistant/views.py)** - All API endpoints + Mock AI service
- **[assistant/admin.py](assistant/admin.py)** - Django admin configuration
- **[assistant/management/commands/populate_products.py](assistant/management/commands/populate_products.py)** - Sample data loader

### Frontend (HTML/CSS/JS)
- **[assistant/templates/assistant/base.html](assistant/templates/assistant/base.html)** - Base layout with CSS
- **[assistant/templates/assistant/index.html](assistant/templates/assistant/index.html)** - Main dashboard with chat, products, and comparison

### Configuration
- **[smart_shopper/settings.py](smart_shopper/settings.py)** - Django settings
- **[smart_shopper/urls.py](smart_shopper/urls.py)** - URL routing
- **[assistant/urls.py](assistant/urls.py)** - App-specific URLs

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main dashboard |
| `/api/search/` | GET | Search products |
| `/api/compare/` | POST | Compare products |
| `/api/recommendations/` | GET | Get recommendations |
| `/api/chat/` | POST | Chat with AI |
| `/api/chat/history/` | GET | Get chat history |
| `/api/preferences/` | POST | Update preferences |

---

## Database Status

✅ Migrations applied: 17 tables created
✅ Products loaded: 20 sample products
   - 5 Laptops
   - 5 Phones
   - 6 Headphones
   - 4 Budget options

---

## Next Steps

1. **Customize Products**: Edit `assistant/management/commands/populate_products.py`
2. **Add Real AI**: See README.md section "Replacing with Real AI"
3. **Style Changes**: Modify CSS in `base.html` or `index.html`
4. **Add Features**: Extend models and views as needed

---

## Troubleshooting

**Port in use?**
```bash
python manage.py runserver 8001
```

**Database error?**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py populate_products
```

**Static files missing?**
```bash
python manage.py collectstatic
```

---

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Mock AI Service (ready for OpenAI/Anthropic integration)

---

**Status**: ✅ Ready to Run!

**Total Development Time**: All phases complete

# Email Marketing Platform

A comprehensive email marketing system built with Django, featuring campaign management, A/B testing, subscriber management, email scheduling, and detailed analytics.

## Features

### Core Features
- ✅ **Campaign Management**: Create, edit, and manage email campaigns
- ✅ **Email Templates**: Build and reuse HTML email templates
- ✅ **Subscriber Management**: Manage subscribers with import/export functionality
- ✅ **Email Lists**: Organize subscribers into targeted lists
- ✅ **Email Scheduling**: Schedule campaigns for future delivery
- ✅ **Analytics Dashboard**: Track opens, clicks, and engagement metrics
- ✅ **A/B Testing**: Test different email variants to optimize performance

### Detailed Features

#### Campaign Management
- Create draft campaigns and schedule them for later
- Support for regular campaigns and A/B test campaigns
- Campaign status tracking (Draft, Scheduled, Sending, Sent, Paused)
- Real-time statistics and performance metrics

#### Email Templates
- Rich HTML editor support
- Subject line management
- Plain text version support
- Template reuse across campaigns
- Active/inactive status management

#### Subscriber Management
- Individual subscriber creation
- Bulk CSV import
- Subscriber status tracking (Active, Unsubscribed, Bounced, Pending)
- Custom fields for segmentation
- Search and filter functionality

#### A/B Testing
- Split test two email variants
- Configurable split percentage
- Variant performance comparison
- Winner selection functionality
- Detailed analytics per variant

#### Analytics
- Email open tracking
- Link click tracking
- Open rate and click rate calculations
- Per-recipient activity logs
- Visual charts and graphs
- A/B test comparison

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd email_marketing_platform
   ```

2. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Set admin password:**
   ```bash
   python manage.py set_admin_password
   ```
   This sets the admin password to `admin123`

6. **(Optional) Populate with dummy data:**
   ```bash
   python manage.py populate_dummy_data
   ```
   This will create:
   - 4 email lists
   - 50 subscribers
   - 5 email templates
   - 6 campaigns (including A/B test)
   - Email logs and analytics

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Or on Windows, simply double-click `run.bat`

8. **Access the application:**
   - Web Interface: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

### Default Login Credentials
- Username: `admin`
- Password: `admin123`

**Note:** Change the default password after first login!

## Usage Guide

### Getting Started Workflow

1. **Create Email Lists**
   - Navigate to Email Lists
   - Create lists for different subscriber segments

2. **Add Subscribers**
   - Manually add individual subscribers
   - Or use bulk import feature (CSV format: email, first_name, last_name)

3. **Create Email Templates**
   - Design your email with HTML
   - Use placeholders: `{{ first_name }}`, `{{ last_name }}`, `{{ email }}`
   - Save and activate templates

4. **Create Campaigns**
   - Choose template and email list
   - Or create A/B test campaign with two variants
   - Schedule or send immediately

5. **Monitor Analytics**
   - Track open rates and click rates
   - For A/B tests, compare variant performance
   - Select winning variant based on data

### A/B Testing Best Practices

1. **Test One Element at a Time**
   - Subject lines
   - Call-to-action buttons
   - Email layout
   - Images vs text

2. **Statistical Significance**
   - Minimum 1000 recipients per variant
   - Wait for sufficient data before deciding

3. **Common Metrics to Track**
   - Open rate (subject line effectiveness)
   - Click rate (content engagement)
   - Conversion rate (if tracking is set up)

## Project Structure

```
email_marketing_platform/
├── email_marketing/          # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── campaigns/               # Core application
│   ├── models.py            # Data models
│   ├── views.py             # View functions
│   ├── forms.py             # Form classes
│   ├── urls.py              # App URLs
│   ├── admin.py             # Admin configuration
│   └── templates/           # HTML templates
│       └── campaigns/
│           ├── base.html
│           ├── dashboard.html
│           ├── email_list_*.html
│           ├── subscriber_*.html
│           ├── template_*.html
│           └── campaign_*.html
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Data Models

### EmailList
- Stores email list/group information
- Tracks creation and modification timestamps

### Subscriber
- Individual subscriber information
- Email, name, status tracking
- Many-to-many relationship with EmailList
- Custom fields support via JSON

### EmailTemplate
- HTML and text email content
- Subject line management
- Reusable across campaigns

### Campaign
- Main campaign entity
- Links template and email list
- A/B testing support
- Scheduling capabilities
- Status tracking

### EmailLog
- Individual email send records
- Status tracking (pending, sent, failed, bounced)
- A/B test variant assignment

### EmailAnalytics
- Open and click tracking
- User agent and IP capture
- Per-recipient engagement data

## Technologies Used

- **Backend**: Django 6.0.1
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5.3
- **Charts**: Chart.js 4.4
- **Icons**: Bootstrap Icons
- **Fonts**: Inter (Google Fonts)
- **Design**: Modern gradient-based UI with animations

## Design Features

### Modern UI/UX
- **Gradient Backgrounds**: Beautiful purple gradient theme
- **Smooth Animations**: Fade-in effects and hover transitions
- **Responsive Design**: Works perfectly on all devices
- **Interactive Elements**: Animated buttons and cards
- **Visual Hierarchy**: Clear information architecture
- **Color-coded Status**: Easy-to-understand badge system

### Dashboard Highlights
- Welcome banner with gradient background
- Animated stat cards with icons
- Quick action cards with hover effects
- Recent activity feeds
- Getting started guide for new users

### Enhanced Components
- **Cards**: Shadow effects and hover animations
- **Buttons**: Gradient backgrounds with ripple effects
- **Tables**: Hover effects and smooth transitions
- **Forms**: Modern input styling with focus states
- **Charts**: Beautiful data visualization
- **Badges**: Gradient backgrounds for status indicators

## Development

### Running Tests
```bash
python manage.py test campaigns
```

### Creating New Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Management Commands
- `set_admin_password` - Reset admin password
- `populate_dummy_data` - Add sample data for testing

### Django Admin
Access the admin panel at `/admin/` for:
- Direct database management
- User management
- Detailed model inspection
- Bulk operations

## Future Enhancements

Potential features for future versions:
- [ ] Email sending integration (SMTP/API)
- [ ] Automated email sequences/drip campaigns
- [ ] Landing page builder
- [ ] Form builder for subscriber signup
- [ ] Advanced segmentation
- [ ] Email preview across devices
- [ ] Integration with email service providers
- [ ] Automated bounce handling
- [ ] Unsubscribe management page
- [ ] Custom domain tracking
- [ ] Webhook integrations
- [ ] REST API for external integrations

## Security Considerations

- Always use HTTPS in production
- Change default admin password
- Implement rate limiting for email sending
- Validate and sanitize all user inputs
- Use environment variables for sensitive data
- Regular security updates

## License

This project is for educational purposes.

## Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the project repository.

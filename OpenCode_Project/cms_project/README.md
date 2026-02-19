# Content Management System (CMS)

A flexible Django CMS for managing various content types including pages, content blocks, templates, media library, navigation, and user roles.

## Features

- **Page Builder**: Create and manage pages with drag-and-drop content blocks
- **Content Blocks**: Support for Text, HTML, Image, Video, Quote, Code, and more
- **Template System**: Create reusable page templates with custom sections
- **Media Library**: Upload and organize media files with folders and collections
- **Navigation Management**: Create custom navigation menus with nested items
- **User Roles**: Define custom roles and permissions for page and media access

## Tech Stack

- Django 5.2
- Python 3.13
- SQLite (default)
- Bootstrap 5

## Installation

1. Navigate to the project directory:
   ```bash
   cd cms_project
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies (if needed):
   ```bash
   pip install django pillow
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the admin panel at: http://127.0.0.1:8000/admin/
8. Access the CMS at: http://127.0.0.1:8000/

## Models

### Pages App
- **Page**: Main page model with title, slug, template, status, meta fields
- **ContentBlock**: Individual content blocks (text, HTML, image, video, etc.)
- **PageRevision**: Version history for pages
- **PageView**: Track page views

### Media App
- **MediaFile**: File uploads with metadata (type, size, dimensions)
- **MediaFolder**: Organize media into folders
- **MediaCollection**: Group media files into collections
- **MediaUsage**: Track where media files are used

### Navigation App
- **Navigation**: Navigation menus
- **NavigationItem**: Individual menu items with hierarchy
- **Breadcrumb**: Custom breadcrumbs for pages
- **FooterLink**: Footer link management

### Templates App
- **Template**: Page templates with types
- **TemplateSection**: Custom sections within templates
- **GlobalBlock**: Reusable content blocks (header, footer, sidebar)
- **Theme**: Site theming with colors and fonts
- **TemplateVariable**: Custom template variables

### Roles App
- **Role**: Custom user roles with permissions
- **RoleAssignment**: Assign roles to users
- **PagePermission**: Per-page access control
- **MediaPermission**: Media folder access control
- **Workflow**: Custom workflows for content approval
- **WorkflowState**: States within workflows
- **WorkflowTransition**: Transitions between workflow states

## Usage

### Creating a Page

1. Navigate to Pages > New Page
2. Fill in the page details (title, slug, template, status)
3. Save the page
4. Click "Builder" to add content blocks
5. Add blocks (Text, Image, HTML, etc.) and arrange them
6. Click "Publish" to make the page live

### Managing Media

1. Go to Media Library
2. Click "Upload Media"
3. Select a file and add metadata
4. Organize files into folders or collections

### Creating Navigation

1. Go to Navigation
2. Create a new navigation menu
3. Add menu items (internal, external, or page links)
4. Set hierarchy with parent-child relationships

### Managing Templates

1. Go to Templates
2. Create a new template with sections
3. Define allowed block types for each section
4. Assign pages to templates

## URLs

- `/` - Page list
- `/page/<slug>/` - View page
- `/builder/<slug>/` - Page builder
- `/media/` - Media library
- `/navigation/` - Navigation menus
- `/templates/` - Templates list
- `/admin/` - Django admin

## Project Structure

```
cms_project/
├── cms_project/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pages/                # Pages and content blocks
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── admin.py
├── media/                # Media library
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── navigation/           # Navigation management
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── templates/            # Template system
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── roles/               # User roles and permissions
│   ├── models.py
│   └── admin.py
├── static/              # Static files
├── media/               # Uploaded media
└── templates/           # HTML templates
    ├── base.html
    ├── pages/
    ├── media/
    └── ...
```

## Extensions

This CMS can be extended with:

1. **Rich Text Editor**: Integrate CKEditor or TinyMCE
2. **Image Cropping**: Add django-image-cropping
3. **S3 Storage**: Use django-storages for cloud storage
4. **REST API**: Build API with Django REST Framework
5. **Real-time Editing**: Use Django Channels
6. **Version Control**: Enhanced version management
7. **Multi-language**: Add django-modeltranslation
8. **SEO Tools**: Advanced meta tag management

## License

This project is for educational purposes.

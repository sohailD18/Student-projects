from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from pages.models import Page, ContentBlock
from media.models import MediaFile, MediaFolder, MediaCollection
from navigation.models import Navigation, NavigationItem, FooterLink
from templates_app.models import Template, TemplateSection, GlobalBlock, Theme
from roles.models import Role, RoleAssignment, PagePermission
from django.db import transaction


class Command(BaseCommand):
    help = 'Load demo content for CMS'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_users_and_roles()
            self.create_media_content()
            self.create_templates_and_themes()
            self.create_navigation_menus()
            self.create_pages_with_content()
        
        self.stdout.write(self.style.SUCCESS('Demo content loaded successfully!'))

    def create_users_and_roles(self):
        self.stdout.write('Creating users and roles...')
        
        admin = User.objects.get_or_create(username='admin')[0]
        editor = User.objects.get_or_create(username='editor', email='editor@cms.com', is_staff=True)[0]
        editor.set_password('editor123')
        editor.save()
        
        author = User.objects.get_or_create(username='author', email='author@cms.com')[0]
        author.set_password('author123')
        author.save()
        
        content_editor_role = Role.objects.get_or_create(
            name='Content Editor',
            slug='content-editor',
            defaults={'description': 'Can edit and publish pages'}
        )[0]
        
        author_role = Role.objects.get_or_create(
            name='Author',
            slug='author',
            defaults={'description': 'Can create and edit own pages'}
        )[0]
        
        RoleAssignment.objects.get_or_create(user=editor, role=content_editor_role)
        RoleAssignment.objects.get_or_create(user=author, role=author_role)

    def create_media_content(self):
        self.stdout.write('Creating media content...')
        
        images_folder = MediaFolder.objects.get_or_create(
            name='Images',
            slug='images',
            created_by=User.objects.first()
        )[0]
        
        documents_folder = MediaFolder.objects.get_or_create(
            name='Documents',
            slug='documents',
            created_by=User.objects.first()
        )[0]
        
        MediaFile.objects.get_or_create(
            title='Company Logo',
            file_type='IMAGE',
            original_filename='logo.png',
            file_size=25600,
            mime_type='image/png',
            folder=images_folder,
            alt_text='Company Logo',
            caption='Our official company logo',
            is_public=True,
            uploaded_by=User.objects.first(),
            defaults={'file': 'media_library/company-logo.png'}
        )
        
        MediaFile.objects.get_or_create(
            title='Product Image',
            file_type='IMAGE',
            original_filename='product.jpg',
            file_size=51200,
            mime_type='image/jpeg',
            folder=images_folder,
            alt_text='Featured Product',
            caption='Our latest product showcase',
            is_public=True,
            uploaded_by=User.objects.first(),
            defaults={'file': 'media_library/product.jpg'}
        )
        
        MediaFile.objects.get_or_create(
            title='Hero Banner',
            file_type='IMAGE',
            original_filename='hero.jpg',
            file_size=102400,
            mime_type='image/jpeg',
            folder=images_folder,
            alt_text='Main Banner',
            caption='Website hero section banner',
            is_public=True,
            uploaded_by=User.objects.first(),
            defaults={'file': 'media_library/hero-banner.jpg'}
        )
        
        MediaFile.objects.get_or_create(
            title='Team Photo',
            file_type='IMAGE',
            original_filename='team.jpg',
            file_size=76800,
            mime_type='image/jpeg',
            folder=images_folder,
            alt_text='Our Team',
            caption='Meet our amazing team',
            is_public=True,
            uploaded_by=User.objects.first(),
            defaults={'file': 'media_library/team.jpg'}
        )
        
        collection = MediaCollection.objects.get_or_create(
            name='Homepage Images',
            defaults={
                'description': 'Images used on the homepage',
                'created_by': User.objects.first()
            }
        )[0]
        
        collection.files.set(MediaFile.objects.filter(folder=images_folder)[:3])

    def create_templates_and_themes(self):
        self.stdout.write('Creating templates and themes...')
        
        home_template = Template.objects.get_or_create(
            name='Homepage',
            slug='homepage',
            template_type='HOME',
            description='Default homepage template with hero section',
            is_default=True,
            created_by=User.objects.first()
        )[0]
        
        TemplateSection.objects.get_or_create(
            template=home_template,
            name='Hero Section',
            identifier='hero',
            defaults={
                'description': 'Top hero banner section',
                'order': 1,
                'allowed_block_types': ['HTML', 'IMAGE']
            }
        )
        
        TemplateSection.objects.get_or_create(
            template=home_template,
            name='Features Section',
            identifier='features',
            defaults={
                'description': 'Features showcase section',
                'order': 2,
                'allowed_block_types': ['TEXT', 'HTML', 'IMAGE']
            }
        )
        
        TemplateSection.objects.get_or_create(
            template=home_template,
            name='CTA Section',
            identifier='cta',
            defaults={
                'description': 'Call to action section',
                'order': 3,
                'allowed_block_types': ['TEXT', 'HTML']
            }
        )
        
        page_template = Template.objects.get_or_create(
            name='Standard Page',
            slug='standard-page',
            template_type='PAGE',
            description='Standard content page template',
            created_by=User.objects.first()
        )[0]
        
        TemplateSection.objects.get_or_create(
            template=page_template,
            name='Main Content',
            identifier='main_content',
            defaults={
                'description': 'Page main content area',
                'order': 1,
                'is_required': True,
                'allowed_block_types': ['TEXT', 'HTML', 'IMAGE', 'VIDEO', 'QUOTE', 'CODE', 'DIVIDER']
            }
        )
        
        GlobalBlock.objects.get_or_create(
            name='Site Header',
            identifier='site-header',
            block_type='HEADER',
            content='''
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="/">CMS</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                </div>
            </nav>
            ''',
            is_active=True,
            created_by=User.objects.first()
        )
        
        GlobalBlock.objects.get_or_create(
            name='Site Footer',
            identifier='site-footer',
            block_type='FOOTER',
            content='''
            <footer class="bg-light text-center py-3">
                <div class="container">
                    <p class="text-muted mb-0">&copy; 2026 CMS. All rights reserved.</p>
                </div>
            </footer>
            ''',
            is_active=True,
            created_by=User.objects.first()
        )
        
        GlobalBlock.objects.get_or_create(
            name='Newsletter Signup',
            identifier='newsletter',
            block_type='PROMO',
            content='<h3>Subscribe to our Newsletter</h3><p>Get the latest updates and news delivered to your inbox.</p>',
            is_active=True,
            created_by=User.objects.first()
        )
        
        Theme.objects.get_or_create(
            name='Default Blue',
            slug='default-blue',
            description='Default blue color theme',
            primary_color='#007bff',
            secondary_color='#6c757d',
            accent_color='#28a745',
            background_color='#ffffff',
            text_color='#333333',
            is_default=True,
            is_active=True,
            created_by=User.objects.first()
        )
        
        Theme.objects.get_or_create(
            name='Dark Mode',
            slug='dark-mode',
            description='Dark color theme',
            primary_color='#6c757d',
            secondary_color='#495057',
            accent_color='#17a2b8',
            background_color='#212529',
            text_color='#ffffff',
            is_default=False,
            is_active=False,
            created_by=User.objects.first()
        )

    def create_navigation_menus(self):
        self.stdout.write('Creating navigation menus...')
        
        main_nav = Navigation.objects.get_or_create(
            name='Main Navigation',
            slug='main-navigation',
            description='Primary website navigation',
            is_active=True,
            created_by=User.objects.first()
        )[0]
        
        home_item = NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Home',
            link_type='INTERNAL',
            url='/',
            order=1,
            is_active=True,
            defaults={'css_classes': 'nav-link-home'}
        )[0]
        
        about_item = NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='About',
            link_type='INTERNAL',
            url='/about/',
            order=2,
            is_active=True
        )[0]
        
        NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Company',
            link_type='INTERNAL',
            url='/about/company/',
            parent=about_item,
            order=1,
            is_active=True
        )
        
        NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Team',
            link_type='INTERNAL',
            url='/about/team/',
            parent=about_item,
            order=2,
            is_active=True
        )
        
        services_item = NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Services',
            link_type='INTERNAL',
            url='/services/',
            order=3,
            is_active=True
        )[0]
        
        NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Web Development',
            link_type='INTERNAL',
            url='/services/web-development/',
            parent=services_item,
            order=1,
            is_active=True
        )
        
        NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Mobile Apps',
            link_type='INTERNAL',
            url='/services/mobile-apps/',
            parent=services_item,
            order=2,
            is_active=True
        )
        
        NavigationItem.objects.get_or_create(
            navigation=main_nav,
            title='Contact',
            link_type='INTERNAL',
            url='/contact/',
            order=4,
            is_active=True
        )
        
        footer_nav = Navigation.objects.get_or_create(
            name='Footer Navigation',
            slug='footer-navigation',
            description='Footer quick links',
            is_active=True,
            created_by=User.objects.first()
        )[0]
        
        FooterLink.objects.get_or_create(
            title='Privacy Policy',
            url='/privacy/',
            group='LEGAL',
            order=1,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Terms of Service',
            url='/terms/',
            group='LEGAL',
            order=2,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Cookie Policy',
            url='/cookies/',
            group='LEGAL',
            order=3,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Contact Us',
            url='/contact/',
            group='COMPANY',
            order=1,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Careers',
            url='/careers/',
            group='COMPANY',
            order=2,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Blog',
            url='/blog/',
            group='RESOURCES',
            order=1,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Documentation',
            url='/docs/',
            group='RESOURCES',
            order=2,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Facebook',
            url='https://facebook.com',
            group='SOCIAL',
            order=1,
            is_active=True
        )
        
        FooterLink.objects.get_or_create(
            title='Twitter',
            url='https://twitter.com',
            group='SOCIAL',
            order=2,
            is_active=True
        )

    def create_pages_with_content(self):
        self.stdout.write('Creating pages with content...')
        
        admin = User.objects.first()
        home_template = Template.objects.filter(slug='homepage').first()
        page_template = Template.objects.filter(slug='standard-page').first()
        
        homepage = Page.objects.get_or_create(
            slug='home',
            defaults={
                'title': 'Welcome to Our CMS',
                'template': home_template,
                'status': 'PUBLISHED',
                'author': admin,
                'meta_title': 'Home - Content Management System',
                'meta_description': 'A powerful and flexible CMS for managing your content',
                'meta_keywords': 'CMS, content management, Django',
                'published_at': timezone.now()
            }
        )[0]
        
        ContentBlock.objects.get_or_create(
            page=homepage,
            block_type='HTML',
            title='Hero Banner',
            order=1,
            defaults={
                'content': '''
                <div class="hero-section bg-primary text-white py-5">
                    <div class="container">
                        <div class="row align-items-center">
                            <div class="col-lg-6">
                                <h1 class="display-4 fw-bold">Build Amazing Websites</h1>
                                <p class="lead">A powerful, flexible CMS that puts you in control of your content.</p>
                                <a href="/contact/" class="btn btn-light btn-lg">Get Started</a>
                            </div>
                            <div class="col-lg-6">
                                <img src="/media/media_library/hero-banner.jpg" class="img-fluid rounded" alt="CMS Hero">
                            </div>
                        </div>
                    </div>
                </div>
                ''',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=homepage,
            block_type='HTML',
            title='Features',
            order=2,
            defaults={
                'content': '''
                <section class="py-5">
                    <div class="container">
                        <h2 class="text-center mb-5">Why Choose Our CMS?</h2>
                        <div class="row">
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-rocket fa-3x text-primary mb-3"></i>
                                        <h4>Fast & Powerful</h4>
                                        <p>Built on Django for speed and scalability. Handle millions of pages with ease.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-puzzle-piece fa-3x text-primary mb-3"></i>
                                        <h4>Flexible Builder</h4>
                                        <p>Drag-and-drop page builder with multiple content blocks.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-shield-alt fa-3x text-primary mb-3"></i>
                                        <h4>Secure</h4>
                                        <p>Enterprise-grade security with role-based access control.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                ''',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=homepage,
            block_type='TEXT',
            title='CTA Section',
            order=3,
            defaults={
                'content': '''
                Ready to get started? Join thousands of satisfied users who trust our CMS for their content management needs. Our team is here to help you succeed with 24/7 support and comprehensive documentation.
                ''',
                'is_active': True
            }
        )
        
        about_page = Page.objects.get_or_create(
            slug='about',
            defaults={
                'title': 'About Us',
                'template': page_template,
                'status': 'PUBLISHED',
                'author': admin,
                'meta_title': 'About Us - CMS',
                'meta_description': 'Learn more about our company and mission',
                'published_at': timezone.now()
            }
        )[0]
        
        ContentBlock.objects.get_or_create(
            page=about_page,
            block_type='TEXT',
            title='Introduction',
            order=1,
            defaults={
                'content': '''
                We are a team of passionate developers and designers committed to building the best content management system. Founded in 2020, we have grown from a small startup to a trusted platform used by thousands of websites worldwide.

                Our mission is simple: empower content creators with tools that are powerful yet easy to use. We believe everyone should be able to build beautiful, functional websites without needing extensive technical knowledge.
                ''',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=about_page,
            block_type='IMAGE',
            title='Team Photo',
            order=2,
            defaults={
                'content': '/media/media_library/team.jpg',
                'css_classes': 'img-fluid rounded mb-4',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=about_page,
            block_type='QUOTE',
            title='Our Mission',
            order=3,
            defaults={
                'content': 'To empower content creators with tools that are powerful yet easy to use.',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=about_page,
            block_type='DIVIDER',
            title='',
            order=4,
            defaults={
                'content': '',
                'is_active': True
            }
        )
        
        services_page = Page.objects.get_or_create(
            slug='services',
            defaults={
                'title': 'Our Services',
                'template': page_template,
                'status': 'PUBLISHED',
                'author': admin,
                'meta_title': 'Services - CMS',
                'meta_description': 'Discover our range of services',
                'published_at': timezone.now()
            }
        )[0]
        
        ContentBlock.objects.get_or_create(
            page=services_page,
            block_type='TEXT',
            title='Services Overview',
            order=1,
            defaults={
                'content': '''
                We offer comprehensive solutions to help you build, manage, and grow your online presence. From web development to digital marketing, our team has the expertise to deliver results.
                ''',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=services_page,
            block_type='HTML',
            title='Services List',
            order=2,
            defaults={
                'content': '''
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <h4><i class="fas fa-code text-primary"></i> Web Development</h4>
                        <p>Custom website development using modern technologies and best practices.</p>
                    </div>
                    <div class="col-md-6 mb-4">
                        <h4><i class="fas fa-mobile-alt text-primary"></i> Mobile Apps</h4>
                        <p>Native and cross-platform mobile application development.</p>
                    </div>
                    <div class="col-md-6 mb-4">
                        <h4><i class="fas fa-search text-primary"></i> SEO Services</h4>
                        <p>Improve your search engine rankings with our proven SEO strategies.</p>
                    </div>
                    <div class="col-md-6 mb-4">
                        <h4><i class="fas fa-chart-line text-primary"></i> Analytics</h4>
                        <p>Data-driven insights to optimize your digital presence.</p>
                    </div>
                </div>
                ''',
                'is_active': True
            }
        )
        
        contact_page = Page.objects.get_or_create(
            slug='contact',
            defaults={
                'title': 'Contact Us',
                'template': page_template,
                'status': 'PUBLISHED',
                'author': admin,
                'meta_title': 'Contact - CMS',
                'meta_description': 'Get in touch with our team',
                'published_at': timezone.now()
            }
        )[0]
        
        ContentBlock.objects.get_or_create(
            page=contact_page,
            block_type='TEXT',
            title='Contact Info',
            order=1,
            defaults={
                'content': '''
                We'd love to hear from you! Whether you have questions about our services, need technical support, or just want to say hello, our team is here to help.
                ''',
                'is_active': True
            }
        )
        
        ContentBlock.objects.get_or_create(
            page=contact_page,
            block_type='HTML',
            title='Contact Form',
            order=2,
            defaults={
                'content': '''
                <div class="row">
                    <div class="col-md-6">
                        <form>
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Subject</label>
                                <input type="text" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message</label>
                                <textarea class="form-control" rows="5" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Send Message</button>
                        </form>
                    </div>
                    <div class="col-md-6">
                        <h4>Contact Information</h4>
                        <p><strong>Email:</strong> info@example.com</p>
                        <p><strong>Phone:</strong> +1 (555) 123-4567</p>
                        <p><strong>Address:</strong> 123 CMS Street, Tech City, TC 12345</p>
                        <hr>
                        <h5>Business Hours</h5>
                        <p>Monday - Friday: 9:00 AM - 6:00 PM</p>
                        <p>Saturday: 10:00 AM - 4:00 PM</p>
                        <p>Sunday: Closed</p>
                    </div>
                </div>
                ''',
                'is_active': True
            }
        )
        
        draft_page = Page.objects.get_or_create(
            slug='blog-draft',
            defaults={
                'title': 'Upcoming Blog Post',
                'template': page_template,
                'status': 'DRAFT',
                'author': User.objects.filter(username='author').first() or admin,
                'meta_title': 'New Feature Announcement - CMS',
                'published_at': None
            }
        )[0]
        
        ContentBlock.objects.get_or_create(
            page=draft_page,
            block_type='TEXT',
            title='Draft Content',
            order=1,
            defaults={
                'content': 'This is a draft page. Publish it when the content is ready for the public.',
                'is_active': True
            }
        )
        
        page_permission = PagePermission.objects.get_or_create(
            page=draft_page,
            user=User.objects.filter(username='author').first() or admin,
            permission='EDIT',
            defaults={'granted_by': admin}
        )
        
        page_permission = PagePermission.objects.get_or_create(
            page=draft_page,
            user=User.objects.filter(username='author').first() or admin,
            permission='PUBLISH',
            defaults={'granted_by': admin}
        )

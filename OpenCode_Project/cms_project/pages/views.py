from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Page, ContentBlock, PageRevision
from .forms import PageForm, ContentBlockForm


def is_editor(user):
    return user.is_authenticated and user.has_perm('pages.change_page')


class PageListView(ListView):
    model = Page
    template_name = 'pages/page_list.html'
    context_object_name = 'pages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Page.objects.all()
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(slug__icontains=search) |
                Q(meta_description__icontains=search)
            )
        
        return queryset.select_related('author', 'template')


class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        if self.object.status == 'PUBLISHED':
            self.object.views.create(
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
        
        return response
    
    def get_queryset(self):
        if self.request.user.has_perm('pages.view_page'):
            return Page.objects.all()
        
        if self.request.user.is_authenticated:
            return Page.objects.filter(
                models.Q(status='PUBLISHED') | 
                models.Q(author=self.request.user)
            )
        
        return Page.objects.filter(status='PUBLISHED')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PageCreateView(CreateView):
    model = Page
    form_class = PageForm
    template_name = 'pages/page_form.html'
    success_url = reverse_lazy('page_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PageUpdateView(UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'pages/page_form.html'
    slug_url_kwarg = 'slug'
    
    def form_valid(self, form):
        old_data = {
            'title': self.object.title,
            'content': [block.content for block in self.object.blocks.all()]
        }
        
        response = super().form_valid(form)
        
        PageRevision.objects.create(
            page=self.object,
            title=self.object.title,
            content_data=old_data,
            created_by=self.request.user,
            notes='Auto-saved revision on update'
        )
        
        return response


class PageDeleteView(DeleteView):
    model = Page
    template_name = 'pages/page_confirm_delete.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('page_list')


@login_required
@user_passes_test(is_editor)
def page_builder(request, slug):
    page = get_object_or_404(Page, slug=slug)
    content_blocks = page.content_blocks
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_block':
            form = ContentBlockForm(request.POST)
            if form.is_valid():
                block = form.save(commit=False)
                block.page = page
                block.save()
                return JsonResponse({'success': True, 'block_id': block.id})
        
        elif action == 'update_block':
            block_id = request.POST.get('block_id')
            block = get_object_or_404(ContentBlock, id=block_id, page=page)
            form = ContentBlockForm(request.POST, instance=block)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
        
        elif action == 'delete_block':
            block_id = request.POST.get('block_id')
            block = get_object_or_404(ContentBlock, id=block_id, page=page)
            block.delete()
            return JsonResponse({'success': True})
        
        elif action == 'reorder_blocks':
            order = request.POST.getlist('order')
            for i, block_id in enumerate(order):
                block = get_object_or_404(ContentBlock, id=block_id, page=page)
                block.order = i
                block.save()
            return JsonResponse({'success': True})
    
    return render(request, 'pages/page_builder.html', {
        'page': page,
        'content_blocks': content_blocks,
        'block_form': ContentBlockForm()
    })


@login_required
def page_revisions(request, slug):
    page = get_object_or_404(Page, slug=slug)
    revisions = page.revisions.all()
    
    if request.method == 'POST' and request.user.has_perm('pages.change_page'):
        revision_id = request.POST.get('revision_id')
        revision = get_object_or_404(PageRevision, id=revision_id, page=page)
        
        page.title = revision.title
        content_data = revision.content_data
        
        page.save()
        
        return redirect('page_builder', slug=page.slug)
    
    return render(request, 'pages/page_revisions.html', {
        'page': page,
        'revisions': revisions
    })

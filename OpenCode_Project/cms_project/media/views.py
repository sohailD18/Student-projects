from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import MediaFile, MediaFolder, MediaCollection
from .forms import MediaFileForm, MediaFolderForm, MediaCollectionForm


class MediaListView(LoginRequiredMixin, ListView):
    model = MediaFile
    template_name = 'media/media_list.html'
    context_object_name = 'media_files'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = MediaFile.objects.select_related('uploaded_by', 'folder').all()
        
        folder_id = self.request.GET.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        file_type = self.request.GET.get('type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = MediaFolder.objects.filter(parent=None)
        context['collections'] = MediaCollection.objects.all()
        return context


class MediaUploadView(LoginRequiredMixin, CreateView):
    model = MediaFile
    form_class = MediaFileForm
    template_name = 'media/media_upload.html'
    success_url = reverse_lazy('media_list')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        
        import os
        file = form.cleaned_data['file']
        filename = file.name
        ext = os.path.splitext(filename)[1].lower()
        
        ext_mapping = {
            '.jpg': 'IMAGE', '.jpeg': 'IMAGE', '.png': 'IMAGE', '.gif': 'IMAGE', '.webp': 'IMAGE',
            '.mp4': 'VIDEO', '.avi': 'VIDEO', '.mov': 'VIDEO', '.wmv': 'VIDEO',
            '.mp3': 'AUDIO', '.wav': 'AUDIO', '.ogg': 'AUDIO',
            '.pdf': 'DOCUMENT', '.doc': 'DOCUMENT', '.docx': 'DOCUMENT', 
            '.xls': 'DOCUMENT', '.xlsx': 'DOCUMENT', '.ppt': 'DOCUMENT', '.pptx': 'DOCUMENT'
        }
        
        form.instance.file_type = ext_mapping.get(ext, 'OTHER')
        form.instance.original_filename = filename
        
        return super().form_valid(form)


class MediaDetailView(LoginRequiredMixin, DetailView):
    model = MediaFile
    template_name = 'media/media_detail.html'
    context_object_name = 'media_file'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.download_count += 1
        self.object.save()
        return response


class MediaUpdateView(LoginRequiredMixin, UpdateView):
    model = MediaFile
    form_class = MediaFileForm
    template_name = 'media/media_form.html'
    success_url = reverse_lazy('media_list')


class MediaDeleteView(LoginRequiredMixin, DeleteView):
    model = MediaFile
    template_name = 'media/media_confirm_delete.html'
    success_url = reverse_lazy('media_list')


class MediaFolderView(LoginRequiredMixin, DetailView):
    model = MediaFolder
    template_name = 'media/media_folder.html'
    context_object_name = 'folder'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subfolders'] = self.object.children.all()
        context['files'] = self.object.files.all()
        return context


class MediaCollectionListView(LoginRequiredMixin, ListView):
    model = MediaCollection
    template_name = 'media/collection_list.html'
    context_object_name = 'collections'


class MediaCollectionCreateView(LoginRequiredMixin, CreateView):
    model = MediaCollection
    form_class = MediaCollectionForm
    template_name = 'media/collection_form.html'
    success_url = reverse_lazy('collection_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@login_required
def media_browser(request):
    files = MediaFile.objects.all()
    folders = MediaFolder.objects.filter(parent=None)
    
    search = request.GET.get('q')
    if search:
        files = files.filter(title__icontains=search)
    
    return render(request, 'media/media_browser.html', {
        'files': files,
        'folders': folders
    })

"""
Django REST Framework API Views for the document system.
"""
import os
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from .models import Category, Document, SearchQuery, DocumentAccess, SystemStats
from .serializers import (
    CategorySerializer, DocumentSerializer, DocumentListSerializer,
    DocumentUploadSerializer, SearchQuerySerializer, DocumentAccessSerializer,
    SystemStatsSerializer, SearchResultSerializer, DashboardStatsSerializer
)
from .text_extraction import TextExtractor
from .classifier import get_classifier
from .search import get_search_engine, preprocess_query


def index_view(request):
    """Serve the main frontend application"""
    return render(request, 'index.html')


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for list views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category CRUD operations"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def with_counts(self, request):
        """Get categories with document counts"""
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document CRUD operations"""
    queryset = Document.objects.select_related('category').all()
    serializer_class = DocumentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'extracted_text']
    filterset_fields = ['file_type', 'category', 'processed']
    ordering_fields = ['title', 'upload_date', 'view_count', 'file_size']
    ordering = ['-upload_date']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'upload':
            return DocumentUploadSerializer
        return DocumentSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload and process a new document

        POST /api/documents/upload/
        Body: multipart/form-data with file, title, description (optional), category (optional)
        """
        serializer = DocumentUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine file type
            ext = file.name.split('.')[-1].lower()
            file_type_map = {'pdf': 'pdf', 'docx': 'docx', 'txt': 'txt'}
            file_type = file_type_map.get(ext, 'txt')

            # Create document
            document = Document(
                title=serializer.validated_data.get('title', file.name),
                description=serializer.validated_data.get('description', ''),
                file=file,
                file_type=file_type,
                file_size=file.size,
                category=serializer.validated_data.get('category'),
                processed=False
            )
            document.save()

            # Process document in background
            self._process_document(document)

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _process_document(self, document: Document):
        """
        Process document: extract text and classify
        """
        # Get file path
        file_path = document.file.path

        # Extract text
        extractor = TextExtractor()
        extracted_text = extractor.extract_text(file_path, document.file_type)
        cleaned_text = extractor.clean_text(extracted_text)

        # Update document with extracted text
        document.extracted_text = cleaned_text[:50000] if cleaned_text else ""  # Limit text length

        # Classify document using ML
        if cleaned_text:
            classifier = get_classifier()
            category_name, confidence = classifier.predict(cleaned_text)

            # Get or create category
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Auto-generated category for {category_name} documents'}
            )

            document.category = category
            document.confidence_score = confidence

        document.processed = True
        document.save()

    @action(detail=True, methods=['post'])
    def reclassify(self, request, pk=None):
        """
        Re-classify a document using ML

        POST /api/documents/{id}/reclassify/
        """
        document = self.get_object()

        if not document.extracted_text:
            return Response(
                {'error': 'No extracted text available for classification'},
                status=status.HTTP_400_BAD_REQUEST
            )

        classifier = get_classifier()
        category_name, confidence = classifier.predict(document.extracted_text)

        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Auto-generated category for {category_name} documents'}
        )

        document.category = category
        document.confidence_score = confidence
        document.save()

        return Response(DocumentSerializer(document).data)

    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """
        Track document view

        POST /api/documents/{id}/track_view/
        """
        document = self.get_object()

        # Increment view count
        document.increment_view_count()

        # Create access log
        DocumentAccess.objects.create(
            document=document,
            access_type='view',
            ip_address=self._get_client_ip(request)
        )

        return Response({'view_count': document.view_count})

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Find similar documents

        GET /api/documents/{id}/similar/?limit=5
        """
        document = self.get_object()
        limit = int(request.query_params.get('limit', 5))

        # Get all documents
        all_documents = list(Document.objects.all())

        # Use search engine to find similar documents
        search_engine = get_search_engine()
        search_engine.initialize_index(all_documents)

        similar_docs = search_engine.get_similar_documents(document, all_documents, limit)

        # Serialize results
        results = []
        for doc, score in similar_docs:
            results.append({
                **DocumentListSerializer(doc).data,
                'similarity_score': score
            })

        return Response(results)


class SearchViewSet(viewsets.ViewSet):
    """ViewSet for intelligent search functionality"""

    def list(self, request):
        """
        Search documents by query

        GET /api/search/?query=keyword&category=Finance&file_type=pdf&limit=20
        """
        query = request.query_params.get('query', '').strip()
        category_filter = request.query_params.get('category')
        file_type_filter = request.query_params.get('file_type')
        limit = int(request.query_params.get('limit', 20))

        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Preprocess query
        processed_query = preprocess_query(query)

        # Get all documents
        documents = list(Document.objects.filter(processed=True).select_related('category'))

        # Initialize search engine
        search_engine = get_search_engine()
        search_engine.initialize_index(documents)

        # Perform search
        results = search_engine.search(
            processed_query,
            documents,
            category_filter,
            file_type_filter,
            limit
        )

        # Track search query
        SearchQuery.objects.create(
            query=processed_query,
            results_count=len(results),
            ip_address=self._get_client_ip(request)
        )

        # Create access logs for search results
        for doc, _ in results:
            DocumentAccess.objects.create(
                document=doc,
                access_type='search_result',
                ip_address=self._get_client_ip(request)
            )

        # Serialize results
        serialized_results = []
        for doc, relevance in results:
            data = DocumentListSerializer(doc).data
            data['relevance_score'] = relevance
            serialized_results.append(data)

        return Response({
            'query': query,
            'results_count': len(serialized_results),
            'results': serialized_results
        })

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DashboardAPIView(APIView):
    """API endpoint for dashboard statistics"""

    def get(self, request):
        """
        Get dashboard statistics

        GET /api/dashboard/
        """
        # Total documents
        total_documents = Document.objects.count()

        # Documents by category
        docs_by_category = list(
            Document.objects.values('category__name', 'category__color')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Documents by type
        docs_by_type = list(
            Document.objects.values('file_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Recent uploads (last 7 days)
        recent_uploads = list(
            Document.objects.select_related('category')
            .filter(upload_date__gte=timezone.now() - timedelta(days=7))
            .order_by('-upload_date')[:10]
        )
        recent_uploads_data = DocumentListSerializer(recent_uploads, many=True).data

        # Top viewed documents
        top_viewed = list(
            Document.objects.select_related('category')
            .order_by('-view_count')[:10]
        )
        top_viewed_data = DocumentListSerializer(top_viewed, many=True).data

        # Total searches
        total_searches = SearchQuery.objects.count()

        # Total categories
        total_categories = Category.objects.count()

        return Response({
            'total_documents': total_documents,
            'documents_by_category': docs_by_category,
            'documents_by_type': docs_by_type,
            'recent_uploads': recent_uploads_data,
            'top_viewed': top_viewed_data,
            'total_searches': total_searches,
            'total_categories': total_categories
        })


class AnalyticsAPIView(APIView):
    """API endpoint for analytics data"""

    def get(self, request):
        """
        Get analytics data

        GET /api/analytics/?days=30
        """
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Search trends
        search_trends = list(
            SearchQuery.objects.filter(executed_at__gte=start_date)
            .annotate(date=TruncDate('executed_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Top search queries
        top_queries = list(
            SearchQuery.objects.filter(executed_at__gte=start_date)
            .values('query')
            .annotate(count=Count('id'), total_results=Sum('results_count'))
            .order_by('-count')[:10]
        )

        # Access patterns by type
        access_patterns = list(
            DocumentAccess.objects.filter(accessed_at__gte=start_date)
            .values('access_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Most accessed documents
        most_accessed = list(
            DocumentAccess.objects.filter(accessed_at__gte=start_date)
            .values('document__title', 'document__id')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        return Response({
            'search_trends': search_trends,
            'top_queries': top_queries,
            'access_patterns': access_patterns,
            'most_accessed': most_accessed
        })


class ReportAPIView(APIView):
    """API endpoint for reporting data"""

    def get(self, request):
        """
        Get reporting data for charts

        GET /api/reports/
        """
        # Document distribution by category
        category_dist = list(
            Document.objects.values('category__name', 'category__color')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Document distribution by type
        type_dist = list(
            Document.objects.values('file_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Upload trends (last 30 days)
        upload_trends = list(
            Document.objects.filter(upload_date__gte=timezone.now() - timedelta(days=30))
            .annotate(date=TruncDate('upload_date'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # View trends (last 30 days)
        view_trends = list(
            DocumentAccess.objects.filter(
                accessed_at__gte=timezone.now() - timedelta(days=30),
                access_type='view'
            )
            .annotate(date=TruncDate('accessed_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        return Response({
            'category_distribution': category_dist,
            'type_distribution': type_dist,
            'upload_trends': upload_trends,
            'view_trends': view_trends
        })

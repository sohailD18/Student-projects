from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LegalDocument, AnalysisReport


def dashboard_view(request):
    """
    Display all uploaded legal documents with their analysis reports.
    """
    documents = LegalDocument.objects.all()

    # Annotate each document with its latest analysis report if exists
    for doc in documents:
        doc.latest_report = doc.analysis_reports.first()
        # Extract just the filename from the full path
        doc.filename = doc.uploaded_file.name.split('/')[-1]

    context = {
        'documents': documents,
        'total_documents': documents.count(),
    }

    return render(request, 'core/dashboard.html', context)


def upload_view(request):
    """
    Handle document upload via POST request.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        uploaded_file = request.FILES.get('document')

        if not title:
            messages.error(request, 'Please provide a document title.')
            return redirect('dashboard')

        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('dashboard')

        # Check file extension
        file_ext = uploaded_file.name.lower().split('.')[-1]
        allowed_extensions = ['pdf', 'docx', 'txt']

        if file_ext not in allowed_extensions:
            messages.error(
                request,
                f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            )
            return redirect('dashboard')

        # Create the document record
        try:
            document = LegalDocument.objects.create(
                title=title,
                uploaded_file=uploaded_file
            )
            messages.success(
                request,
                f'Document "{title}" uploaded successfully.'
            )
            return redirect('dashboard')

        except Exception as e:
            messages.error(
                request,
                f'Error uploading document: {str(e)}'
            )
            return redirect('dashboard')

    # If GET request, redirect to dashboard
    return redirect('dashboard')


def detail_view(request, document_id):
    """
    Display detailed analysis of a specific legal document.
    Extracts text and runs analysis using analyze_document_text.
    """
    from django.http import Http404
    from .utils import extract_text_from_file, analyze_document_text

    # Get the document or return 404
    try:
        document = LegalDocument.objects.get(id=document_id)
        document.filename = document.uploaded_file.name.split('/')[-1]
    except LegalDocument.DoesNotExist:
        raise Http404(f"Document with ID {document_id} not found.")

    # Get existing analysis report if available
    existing_report = document.analysis_reports.first()

    # If no existing report, perform analysis
    analysis = None
    if existing_report:
        # Load from database
        analysis = {
            'risk_level': existing_report.risk_level,
            'key_clauses': [],  # Would need to store these separately if needed
            'missing_clauses': [],  # Would need to store these separately if needed
            'summary': existing_report.summary,
        }
    else:
        # Perform new analysis
        try:
            # Extract text from the uploaded file
            file_path = document.uploaded_file.path
            extracted_text = extract_text_from_file(file_path)

            # Analyze the text
            analysis = analyze_document_text(extracted_text)

            # Save analysis to database
            report = AnalysisReport.objects.create(
                document=document,
                risk_level=analysis['risk_level'],
                summary=analysis['summary'],
                is_compliant=(analysis['risk_level'] == 'LOW')
            )

        except Exception as e:
            messages.error(request, f'Error analyzing document: {str(e)}')
            analysis = None

    context = {
        'document': document,
        'analysis': analysis,
        'has_existing_report': existing_report is not None,
    }

    return render(request, 'core/detail.html', context)


def comparison_view(request):
    """
    Compare two legal documents side by side.
    POST: Process the comparison using compare_texts function.
    GET: Display the document selection form.
    """
    from .utils import extract_text_from_file, compare_texts

    # Get all documents for the selection form
    documents = LegalDocument.objects.all()

    comparison_result = None
    doc1 = None
    doc2 = None

    if request.method == 'POST':
        doc1_id = request.POST.get('document1')
        doc2_id = request.POST.get('document2')

        # Validate document selection
        if not doc1_id or not doc2_id:
            messages.error(request, 'Please select two documents to compare.')
            return render(request, 'core/compare.html', {'documents': documents})

        if doc1_id == doc2_id:
            messages.error(request, 'Please select two different documents to compare.')
            return render(request, 'core/compare.html', {'documents': documents})

        # Get the documents
        try:
            doc1 = LegalDocument.objects.get(id=doc1_id)
            doc2 = LegalDocument.objects.get(id=doc2_id)
        except LegalDocument.DoesNotExist:
            messages.error(request, 'One or both documents not found.')
            return render(request, 'core/compare.html', {'documents': documents})

        # Extract text from both documents
        try:
            text1 = extract_text_from_file(doc1.uploaded_file.path)
            text2 = extract_text_from_file(doc2.uploaded_file.path)

            # Compare the texts
            comparison_result = compare_texts(text1, text2)

        except Exception as e:
            messages.error(request, f'Error comparing documents: {str(e)}')
            comparison_result = None

    context = {
        'documents': documents,
        'comparison_result': comparison_result,
        'doc1': doc1,
        'doc2': doc2,
    }

    return render(request, 'core/compare.html', context)

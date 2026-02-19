import os
from pathlib import Path


def extract_text_from_file(file_path):
    """
    Extract text from a file based on its extension.
    Supports: .pdf, .docx, .txt

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        str: Extracted text content

    Raises:
        ValueError: If file type is not supported
        Exception: For file reading errors
    """
    file_path = Path(file_path)
    file_extension = file_path.suffix.lower()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_extension == '.txt':
        return _extract_from_txt(file_path)
    elif file_extension == '.pdf':
        return _extract_from_pdf(file_path)
    elif file_extension == '.docx':
        return _extract_from_docx(file_path)
    else:
        raise ValueError(
            f"Unsupported file type: {file_extension}. "
            f"Supported types: .pdf, .docx, .txt"
        )


def _extract_from_txt(file_path):
    """Extract text from a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def _extract_from_pdf(file_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError(
            "PyPDF2 is not installed. "
            "Install it with: pip install PyPDF2"
        )

    text = []
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text.append(page.extract_text())

        return '\n'.join(text)
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")


def _extract_from_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    try:
        import docx
    except ImportError:
        raise ImportError(
            "python-docx is not installed. "
            "Install it with: pip install python-docx"
        )

    try:
        doc = docx.Document(file_path)
        text = []

        for paragraph in doc.paragraphs:
            text.append(paragraph.text)

        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text.append(cell.text)

        return '\n'.join(text)
    except Exception as e:
        raise Exception(f"Error reading DOCX file: {str(e)}")


def analyze_document_text(text):
    """
    Analyze legal document text using regex and keyword matching.

    Args:
        text (str): The extracted text from a legal document

    Returns:
        dict: Analysis results containing:
            - risk_level (str): 'HIGH', 'MEDIUM', or 'LOW'
            - key_clauses (list): List of clause names found in document
            - missing_clauses (list): List of required clauses not found
            - summary (str): 3-sentence summary of the document
    """
    import re

    # Standard legal clause checklist
    STANDARD_CLAUSES = {
        'Termination': r'\bterminat(?:e|ion)\b',
        'Indemnification': r'\bindemnif(?:y|ication)\b',
        'Confidentiality': r'\bconfidential(?:ity)?\b|\bnondisclosure\b|\bnon-disclosure\b',
        'Governing Law': r'\bgoverning\s+law\b|\bjurisdiction\b',
        'Force Majeure': r'\bforce\s+majeure\b',
        'Payment Terms': r'\bpayment\s+terms?\b|\bbilling\b',
        'Liability': r'\bliability\b|\blimitation\s+of\s+liability\b',
        'Dispute Resolution': r'\bdispute\s+resolution\b|\barbitration\b|\bmediation\b',
        'Intellectual Property': r'\bintellectual\s+property\b|\bIP\s+rights?\b',
        'Non-Compete': r'\bnon-?\s*compete\b',
        'Severability': r'\bseverability\b',
        'Amendment': r'\bamendment\b|\bmodification\b',
        'Assignment': r'\bassignment\b',
        'Notices': r'\bnotices?\b',
    }

    # High-risk keywords (increase risk level)
    HIGH_RISK_KEYWORDS = [
        r'\bas[-\s]?is\b',
        r'\bno\s+warranty\b',
        r'\bunlimited\s+liability\b',
        r'\bpersonal\s+guarantee\b',
        r'\bpenalt(?:y|ies)\b',
        r'\bterminate\s+without\s+cause\b',
        r'\bexclusive\s+jurisdiction\b',
    ]

    # Find key clauses present in document
    key_clauses = []
    missing_clauses = []

    for clause_name, pattern in STANDARD_CLAUSES.items():
        if re.search(pattern, text, re.IGNORECASE):
            key_clauses.append(clause_name)
        else:
            missing_clauses.append(clause_name)

    # Determine risk level
    high_risk_count = 0
    for keyword in HIGH_RISK_KEYWORDS:
        if re.search(keyword, text, re.IGNORECASE):
            high_risk_count += 1

    # Calculate risk level based on:
    # 1. Number of high-risk keywords found
    # 2. Percentage of missing clauses
    missing_ratio = len(missing_clauses) / len(STANDARD_CLAUSES)

    if high_risk_count >= 3 or missing_ratio > 0.5:
        risk_level = 'HIGH'
    elif high_risk_count >= 1 or missing_ratio > 0.25:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    # Generate a 3-sentence summary
    summary = generate_summary(text, key_clauses, missing_clauses, risk_level)

    return {
        'risk_level': risk_level,
        'key_clauses': key_clauses,
        'missing_clauses': missing_clauses,
        'summary': summary,
    }


def generate_summary(text, key_clauses, missing_clauses, risk_level):
    """
    Generate a 3-sentence summary of the document.

    Args:
        text (str): The document text
        key_clauses (list): Clauses found
        missing_clauses (list): Clauses missing
        risk_level (str): Risk level

    Returns:
        str: 3-sentence summary
    """
    import re

    # Extract first meaningful sentence for context
    sentences = re.split(r'[.!?]+', text)
    first_sentence = "This document appears to be a legal agreement."

    for sent in sentences[:5]:
        sent = sent.strip()
        if len(sent) > 20 and len(sent) < 200:
            first_sentence = sent.strip() + "."
            break

    # Estimate document length
    word_count = len(text.split())
    doc_length = "short" if word_count < 500 else "lengthy" if word_count > 2000 else "moderate-length"

    # Build sentence 2: Clauses analysis
    if len(key_clauses) >= 10:
        clauses_sentence = (
            f"The document includes {len(key_clauses)} standard legal clauses, "
            f"indicating a comprehensive agreement with most key provisions covered."
        )
    elif len(key_clauses) >= 6:
        clauses_sentence = (
            f"The document contains {len(key_clauses)} standard clauses, "
            f"covering several important legal aspects."
        )
    else:
        clauses_sentence = (
            f"The document includes only {len(key_clauses)} standard legal clauses, "
            f"which may indicate a simplified or incomplete agreement."
        )

    # Build sentence 3: Risk and recommendations
    if risk_level == 'HIGH':
        risk_sentence = (
            f"Risk assessment is {risk_level} due to {len(missing_clauses)} missing clauses "
            f"and concerning terms that require immediate legal review."
        )
    elif risk_level == 'MEDIUM':
        risk_sentence = (
            f"Risk assessment is {risk_level} with {len(missing_clauses)} potentially "
            f"missing clauses that should be reviewed."
        )
    else:
        risk_sentence = (
            f"Risk assessment is {risk_level} as the document includes most standard "
            f"clauses, though legal consultation is still recommended."
        )

    return f"{first_sentence} {clauses_sentence} {risk_sentence}"


def compare_texts(text1, text2):
    """
    Compare two texts and return differences.

    Args:
        text1 (str): First text (primary)
        text2 (str): Second text (comparison)

    Returns:
        dict: Comparison results containing:
            - word_count_diff (int): Difference in word count (text1 - text2)
            - text1_word_count (int): Word count of text1
            - text2_word_count (int): Word count of text2
            - unique_words_text1 (list): Words found in text1 but not in text2
            - unique_words_text2 (list): Words found in text2 but not in text1
    """
    import re

    # Extract words from both texts (lowercase, remove punctuation)
    def extract_words(text):
        # Find all word characters, convert to lowercase
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words), len(words)

    words1_set, count1 = extract_words(text1)
    words2_set, count2 = extract_words(text2)

    # Find unique words in each text
    unique_to_text1 = sorted(words1_set - words2_set)
    unique_to_text2 = sorted(words2_set - words1_set)

    return {
        'word_count_diff': count1 - count2,
        'text1_word_count': count1,
        'text2_word_count': count2,
        'unique_words_text1': unique_to_text1,
        'unique_words_text2': unique_to_text2,
    }

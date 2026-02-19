"""
Intelligent search system using TF-IDF vectorization for semantic-like search.
"""
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import Document


class IntelligentSearch:
    """
    TF-IDF based intelligent search that ranks documents by relevance.
    Supports both text content search and metadata filtering.
    """

    def __init__(self, max_features: int = 5000):
        """
        Initialize search engine

        Args:
            max_features: Maximum number of TF-IDF features
        """
        self.max_features = max_features
        self.vectorizer = None
        self.document_vectors = None
        self.document_ids = []
        self._initialized = False

    def _build_corpus(self, documents: List[Document]) -> List[str]:
        """
        Build text corpus from documents

        Args:
            documents: List of Document objects

        Returns:
            List of text content for each document
        """
        corpus = []
        self.document_ids = []

        for doc in documents:
            # Combine title, description, and extracted text
            text_parts = []

            if doc.title:
                # Boost title weight by repeating it
                text_parts.extend([doc.title] * 3)

            if doc.description:
                text_parts.append(doc.description)

            if doc.extracted_text:
                text_parts.append(doc.extracted_text)

            # Add category if available
            if doc.category:
                text_parts.append(doc.category.name)

            combined_text = ' '.join(text_parts)
            corpus.append(combined_text)
            self.document_ids.append(doc.id)

        return corpus

    def initialize_index(self, documents: List[Document]):
        """
        Build or rebuild the search index

        Args:
            documents: List of all documents to index
        """
        if not documents:
            self._initialized = False
            return

        # Build corpus
        corpus = self._build_corpus(documents)

        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            stop_words='english',
            lowercase=True
        )

        # Fit and transform corpus
        self.document_vectors = self.vectorizer.fit_transform(corpus)
        self._initialized = True

    def search(
        self,
        query: str,
        documents: List[Document],
        category_filter: Optional[str] = None,
        file_type_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[Tuple[Document, float]]:
        """
        Search documents by query with optional filters

        Args:
            query: Search query
            documents: List of documents to search
            category_filter: Optional category name filter
            file_type_filter: Optional file type filter
            limit: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples, sorted by relevance
        """
        if not query or not query.strip():
            return []

        # Initialize index if needed or if documents changed
        if not self._initialized or len(documents) != len(self.document_ids):
            self.initialize_index(documents)

        if not self._initialized:
            # Fallback: simple keyword search
            return self._keyword_search(query, documents, category_filter, file_type_filter, limit)

        # Apply filters
        filtered_docs = documents
        if category_filter:
            filtered_docs = [d for d in filtered_docs if d.category and d.category.name == category_filter]
        if file_type_filter:
            filtered_docs = [d for d in filtered_docs if d.file_type == file_type_filter]

        if not filtered_docs:
            return []

        # Transform query
        query_vector = self.vectorizer.transform([query])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]

        # Create list of (doc_id, similarity) and sort
        doc_similarity = list(zip(self.document_ids, similarities))

        # Filter to only documents in our filtered set
        filtered_ids = {d.id for d in filtered_docs}
        doc_similarity = [(doc_id, sim) for doc_id, sim in doc_similarity if doc_id in filtered_ids]

        # Sort by similarity (descending)
        doc_similarity.sort(key=lambda x: x[1], reverse=True)

        # Get top results
        results = []
        for doc_id, similarity in doc_similarity[:limit]:
            if similarity > 0:  # Only include matches with some relevance
                # Find the document object
                doc = next((d for d in documents if d.id == doc_id), None)
                if doc:
                    results.append((doc, float(similarity)))

        return results

    def _keyword_search(
        self,
        query: str,
        documents: List[Document],
        category_filter: Optional[str] = None,
        file_type_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[Tuple[Document, float]]:
        """
        Fallback keyword-based search

        Args:
            query: Search query
            documents: List of documents to search
            category_filter: Optional category name filter
            file_type_filter: Optional file type filter
            limit: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples
        """
        query_lower = query.lower()
        query_terms = query_lower.split()

        results = []

        for doc in documents:
            # Apply filters
            if category_filter and (not doc.category or doc.category.name != category_filter):
                continue
            if file_type_filter and doc.file_type != file_type_filter:
                continue

            # Calculate keyword match score
            score = 0.0

            # Check title (weighted higher)
            if doc.title:
                title_lower = doc.title.lower()
                for term in query_terms:
                    if term in title_lower:
                        score += 3.0

            # Check description
            if doc.description:
                desc_lower = doc.description.lower()
                for term in query_terms:
                    if term in desc_lower:
                        score += 2.0

            # Check extracted text
            if doc.extracted_text:
                text_lower = doc.extracted_text.lower()
                for term in query_terms:
                    if term in text_lower:
                        score += 1.0

            if score > 0:
                results.append((doc, min(score, 1.0)))  # Cap at 1.0

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def get_similar_documents(
        self,
        document: Document,
        documents: List[Document],
        limit: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Find documents similar to a given document

        Args:
            document: Reference document
            documents: List of all documents
            limit: Maximum number of results

        Returns:
            List of (Document, similarity_score) tuples
        """
        if not self._initialized or not document.extracted_text:
            return []

        # Find document index
        try:
            doc_index = self.document_ids.index(document.id)
        except ValueError:
            return []

        # Get document vector
        doc_vector = self.document_vectors[doc_index:doc_index+1]

        # Calculate similarities with all documents
        similarities = cosine_similarity(doc_vector, self.document_vectors)[0]

        # Create list and sort (exclude the document itself)
        doc_similarity = []
        for i, (doc_id, sim) in enumerate(zip(self.document_ids, similarities)):
            if doc_id != document.id:  # Exclude self
                doc = next((d for d in documents if d.id == doc_id), None)
                if doc and sim > 0:
                    doc_similarity.append((doc, float(sim)))

        # Sort by similarity descending
        doc_similarity.sort(key=lambda x: x[1], reverse=True)

        return doc_similarity[:limit]


# Singleton instance
_search_instance = None


def get_search_engine() -> IntelligentSearch:
    """Get or create singleton search engine instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = IntelligentSearch()
    return _search_instance


def preprocess_query(query: str) -> str:
    """
    Clean and preprocess search query

    Args:
        query: Raw query string

    Returns:
        Cleaned query
    """
    if not query:
        return ""

    # Remove special characters but keep spaces and alphanumeric
    query = re.sub(r'[^\w\s]', ' ', query)

    # Remove extra whitespace
    query = ' '.join(query.split())

    return query.strip()


def extract_search_terms(query: str) -> List[str]:
    """
    Extract individual search terms from query

    Args:
        query: Search query

    Returns:
        List of search terms
    """
    query = preprocess_query(query)
    if not query:
        return []

    # Split and filter empty terms
    terms = [t.lower() for t in query.split() if len(t) > 2]
    return terms

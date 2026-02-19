"""
Machine Learning Document Classifier using Naive Bayes and SVM.
Uses scikit-learn for local classification without external APIs.
"""
import os
import pickle
import numpy as np
from typing import List, Tuple, Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)


class DocumentClassifier:
    """
    Document classification using TF-IDF vectorization and Naive Bayes/SVM
    Supports categories: Finance, HR, Legal, Technical, and General
    """

    # Default categories and their associated keywords
    CATEGORY_KEYWORDS = {
        'Finance': [
            'budget', 'financial', 'cost', 'revenue', 'expense', 'profit',
            'investment', 'audit', 'tax', 'accounting', 'invoice', 'payment',
            'salary', 'payroll', 'fiscal', 'monetary', 'currency', 'dollar',
            'market', 'stock', 'dividend', 'capital', 'asset', 'liability',
            'balance', 'sheet', 'income', 'statement', 'cash', 'flow',
            'refund', 'transaction', 'bank', 'credit', 'debit', 'loan'
        ],
        'HR': [
            'employee', 'recruitment', 'hiring', 'training', 'onboarding',
            'performance', 'review', 'leave', 'attendance', 'policy',
            'benefit', 'compensation', 'workplace', 'culture', 'team',
            'termination', 'resignation', 'promotion', 'discipline', 'grievance',
            'human', 'resource', 'personnel', 'staff', 'workforce', 'applicant'
        ],
        'Legal': [
            'contract', 'agreement', 'law', 'legal', 'attorney', 'lawyer',
            'litigation', 'court', 'jurisdiction', 'statute', 'regulation',
            'compliance', 'liability', 'indemnification', 'dispute', 'resolution',
            'intellectual', 'property', 'patent', 'trademark', 'copyright',
            'confidentiality', 'non-disclosure', 'terms', 'conditions', 'clause'
        ],
        'Technical': [
            'software', 'hardware', 'development', 'programming', 'code',
            'algorithm', 'database', 'api', 'system', 'architecture',
            'specification', 'requirement', 'testing', 'deployment', 'server',
            'network', 'protocol', 'technology', 'framework', 'library',
            'function', 'method', 'class', 'object', 'variable', 'documentation',
            'engineering', 'technical', 'debugging', 'integration', 'interface'
        ],
        'General': [
            'report', 'memo', 'announcement', 'update', 'information',
            'procedure', 'guideline', 'manual', 'handbook', 'document'
        ]
    }

    def __init__(self, model_type: str = 'naive_bayes'):
        """
        Initialize classifier

        Args:
            model_type: 'naive_bayes' or 'svm'
        """
        self.model_type = model_type
        self.pipeline = None
        self.categories = list(self.CATEGORY_KEYWORDS.keys())
        self.is_trained = False

        # Initialize stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()

        # Build initial model
        self._build_pipeline()

    def _build_pipeline(self):
        """Build the ML pipeline"""
        if self.model_type == 'svm':
            classifier = SVC(
                kernel='linear',
                probability=True,
                random_state=42,
                C=1.0
            )
        else:  # naive_bayes
            classifier = MultinomialNB(alpha=0.1)

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=2,
                max_df=0.8
            )),
            ('classifier', classifier)
        ])

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for classification

        Args:
            text: Raw text

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep words
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def create_synthetic_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Create synthetic training data from category keywords.
        This allows the classifier to work without manual training.

        Returns:
            Tuple of (texts, labels)
        """
        texts = []
        labels = []

        # Create synthetic documents for each category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            # Create multiple synthetic samples per category
            for i in range(50):
                # Mix and match keywords
                selected_keywords = np.random.choice(keywords, size=min(20, len(keywords)), replace=False)

                # Create a synthetic document
                if category == 'Finance':
                    template = f"Financial Report {i+1}: The {selected_keywords[0]} for this quarter shows {selected_keywords[1]} changes. We need to review the {selected_keywords[2]} and consider {selected_keywords[3]} implications. The {selected_keywords[4]} department has submitted their {selected_keywords[5]} regarding {selected_keywords[6]}."
                elif category == 'HR':
                    template = f"HR Memorandum {i+1}: Regarding {selected_keywords[0]} policy updates. All employees must complete the new {selected_keywords[1]} process. The {selected_keywords[2]} committee will review {selected_keywords[3]} procedures. Please contact {selected_keywords[4]} for questions about {selected_keywords[5]}."
                elif category == 'Legal':
                    template = f"Legal Notice {i+1}: This {selected_keywords[0]} concerns {selected_keywords[1]} matters. The {selected_keywords[2]} requires compliance with {selected_keywords[3]}. Any {selected_keywords[4]} must be reported to {selected_keywords[5]}. This {selected_keywords[6]} is binding."
                elif category == 'Technical':
                    template = f"Technical Specification {i+1}: The {selected_keywords[0]} {selected_keywords[1]} requires implementation of {selected_keywords[2]}. The {selected_keywords[3]} uses {selected_keywords[4]} architecture. Ensure {selected_keywords[5]} compatibility with {selected_keywords[6]}. The {selected_keywords[7]} method handles {selected_keywords[8]}."
                else:  # General
                    template = f"Document {i+1}: This {selected_keywords[0]} provides {selected_keywords[1]} about {selected_keywords[2]}. Please follow the {selected_keywords[3]} for {selected_keywords[4]}. Contact administration for {selected_keywords[5]}."

                texts.append(template)
                labels.append(category)

        return texts, labels

    def train(self, texts: Optional[List[str]] = None, labels: Optional[List[str]] = None):
        """
        Train the classifier. If no data provided, uses synthetic training data.

        Args:
            texts: Optional list of training texts
            labels: Optional list of training labels
        """
        if texts is None or labels is None:
            texts, labels = self.create_synthetic_training_data()

        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]

        # Train the pipeline
        self.pipeline.fit(processed_texts, labels)
        self.is_trained = True

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict category for a single document

        Args:
            text: Document text

        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        if not self.is_trained:
            self.train()

        if not text:
            return 'General', 0.0

        # Preprocess
        processed_text = self.preprocess_text(text)

        # Predict
        prediction = self.pipeline.predict([processed_text])[0]

        # Get probability/confidence
        if hasattr(self.pipeline.named_steps['classifier'], 'predict_proba'):
            probabilities = self.pipeline.predict_proba([processed_text])[0]
            confidence = float(max(probabilities))
        else:
            confidence = 0.7  # Default confidence for SVM without probability

        return prediction, confidence

    def predict_proba_all(self, text: str) -> Dict[str, float]:
        """
        Get probability scores for all categories

        Args:
            text: Document text

        Returns:
            Dictionary mapping category to probability
        """
        if not self.is_trained:
            self.train()

        if not text:
            return {cat: 0.0 for cat in self.categories}

        processed_text = self.preprocess_text(text)

        if hasattr(self.pipeline.named_steps['classifier'], 'predict_proba'):
            probabilities = self.pipeline.predict_proba([processed_text])[0]
            return dict(zip(self.categories, [float(p) for p in probabilities]))
        else:
            # Fallback for SVM
            prediction = self.pipeline.predict([processed_text])[0]
            result = {cat: 0.0 for cat in self.categories}
            result[prediction] = 0.8
            return result

    def save_model(self, filepath: str):
        """Save trained model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'pipeline': self.pipeline,
                'model_type': self.model_type,
                'is_trained': self.is_trained,
                'categories': self.categories
            }, f)

    def load_model(self, filepath: str):
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.pipeline = data['pipeline']
            self.model_type = data['model_type']
            self.is_trained = data['is_trained']
            self.categories = data['categories']


# Singleton instance for application-wide use
_classifier_instance = None


def get_classifier() -> DocumentClassifier:
    """Get or create singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DocumentClassifier()
        _classifier_instance.train()
    return _classifier_instance

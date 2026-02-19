"""
AI Analysis Engine for Meeting Transcript Analysis.
Uses simulated AI logic with regex patterns and NLP-like techniques.
"""
import re
from collections import Counter
from typing import List, Dict, Tuple


class MeetingAnalyzer:
    """
    Main class for analyzing meeting transcripts.
    """

    # Keywords for identifying action items
    ACTION_KEYWORDS = [
        'to do', 'todo', 'action', 'assign', 'will', 'shall',
        'need to', 'has to', 'must', 'deadline', 'due date',
        'responsible', 'follow up', 'next step', 'task',
        'complete', 'finish', 'deliver', 'implement', 'review'
    ]

    # Positive sentiment words
    POSITIVE_WORDS = [
        'good', 'great', 'excellent', 'happy', 'pleased',
        'agree', 'success', 'progress', 'improvement', 'achievement',
        'opportunity', 'collaboration', 'effective', 'efficient',
        'productive', 'accomplish', 'solution', 'innovation'
    ]

    # Negative sentiment words
    NEGATIVE_WORDS = [
        'bad', 'poor', 'terrible', 'unhappy', 'disappointed',
        'disagree', 'failure', 'problem', 'issue', 'concern',
        'delay', 'challenge', 'difficult', 'obstacle', 'risk',
        'worry', 'frustrating', 'confusing', 'unclear', 'lack'
    ]

    # Important keywords for summary generation
    IMPORTANT_KEYWORDS = [
        'decision', 'agreed', 'concluded', 'summary', 'result',
        'outcome', 'plan', 'strategy', 'goal', 'objective',
        'budget', 'timeline', 'deadline', 'milestone', 'launch',
        'development', 'production', 'testing', 'deployment'
    ]

    def __init__(self, transcript: str, duration_minutes: int):
        """
        Initialize the analyzer with transcript and duration.
        """
        self.transcript = transcript.strip() if transcript else ""
        self.duration = duration_minutes
        self.sentences = self._split_into_sentences()
        self.words = self._extract_words()

    def _split_into_sentences(self) -> List[str]:
        """
        Split transcript into sentences using regex.
        """
        if not self.transcript:
            return []

        # Split on common sentence terminators
        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\s*$',
            self.transcript
        )
        return [s.strip() for s in sentences if s.strip()]

    def _extract_words(self) -> List[str]:
        """
        Extract words from transcript, converting to lowercase.
        """
        if not self.transcript:
            return []

        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z]+\b', self.transcript.lower())
        return words

    def extract_action_items(self) -> List[Dict[str, str]]:
        """
        Extract action items from the transcript.
        Returns list of dictionaries with description and assignee.
        """
        action_items = []

        for sentence in self.sentences:
            sentence_lower = sentence.lower()

            # Check if sentence contains action keywords
            if any(keyword in sentence_lower for keyword in self.ACTION_KEYWORDS):
                # Try to extract assignee (looks for patterns like "John will", "assigned to Mary")
                assignee = self._extract_assignee(sentence)

                action_items.append({
                    'description': sentence,
                    'assignee': assignee
                })

        return action_items

    def _extract_assignee(self, sentence: str) -> str:
        """
        Try to extract an assignee name from a sentence.
        Looks for patterns like "John will", "assigned to Mary", etc.
        """
        # Pattern: "assigned to [Name]", "[Name] will", etc.
        patterns = [
            r'assigned to\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s+will',
            r'([A-Z][a-z]+)\s+shall',
            r'([A-Z][a-z]+)\s+needs?\s+to',
            r'([A-Z][a-z]+)\s+is\s+responsible',
        ]

        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()

        return ""

    def generate_summary(self) -> str:
        """
        Generate a summary of the meeting.
        Returns sentences with highest keyword density.
        """
        if not self.sentences:
            return "No transcript available for summary."

        # Score each sentence based on keyword density
        sentence_scores = []

        for i, sentence in enumerate(self.sentences):
            words_in_sentence = [w.lower() for w in re.findall(r'\b[a-zA-Z]+\b', sentence)]

            # Count important keywords
            keyword_count = sum(
                1 for word in words_in_sentence
                if word in self.IMPORTANT_KEYWORDS
            )

            # Score: keyword count / sentence length (normalized)
            score = keyword_count / max(len(words_in_sentence), 1)
            sentence_scores.append((sentence, score, i))

        # Sort by score and take top sentences (up to 3)
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = sentence_scores[:3]

        # Sort by original position to maintain flow
        top_sentences.sort(key=lambda x: x[2])

        summary_sentences = [s[0] for s in top_sentences]

        # If no important keywords found, return first 3 sentences
        if not summary_sentences:
            summary_sentences = self.sentences[:3]

        return " ".join(summary_sentences)

    def analyze_sentiment(self) -> Tuple[str, float]:
        """
        Analyze the sentiment of the transcript.
        Returns (sentiment_label, sentiment_score) where score is -1 to 1.
        """
        if not self.words:
            return "Neutral", 0.0

        positive_count = sum(1 for word in self.words if word in self.POSITIVE_WORDS)
        negative_count = sum(1 for word in self.words if word in self.NEGATIVE_WORDS)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return "Neutral", 0.0

        # Calculate score: -1 (very negative) to 1 (very positive)
        sentiment_score = (positive_count - negative_count) / total_sentiment_words

        # Determine label
        if sentiment_score > 0.2:
            sentiment_label = "Positive"
        elif sentiment_score < -0.2:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        return sentiment_label, round(sentiment_score, 3)

    def calculate_productivity_score(self, action_items_count: int) -> float:
        """
        Calculate productivity score based on multiple factors.
        Score is 0-100.
        """
        if not self.transcript or self.duration == 0:
            return 0.0

        word_count = len(self.words)

        # Factors:
        # 1. Action items per minute (ideal: 1-2 per minute)
        actions_per_minute = action_items_count / max(self.duration, 1)
        action_score = min(actions_per_minute / 2, 1) * 30  # Max 30 points

        # 2. Word density (words per minute)
        words_per_minute = word_count / max(self.duration, 1)
        # Ideal: 100-150 words per minute
        if 100 <= words_per_minute <= 150:
            density_score = 25
        elif words_per_minute > 150:
            # Too verbose might reduce productivity
            density_score = max(25 - (words_per_minute - 150) * 0.1, 10)
        else:
            # Too brief
            density_score = min(words_per_minute / 4, 25)

        # 3. Content richness (unique words ratio)
        if word_count > 0:
            unique_ratio = len(set(self.words)) / word_count
            richness_score = unique_ratio * 25  # Max 25 points
        else:
            richness_score = 0

        # 4. Meeting length efficiency
        if self.duration <= 30:
            length_score = 20  # Short meetings are more efficient
        elif self.duration <= 60:
            length_score = 15
        else:
            length_score = 10

        productivity_score = action_score + density_score + richness_score + length_score

        return round(min(productivity_score, 100), 2)

    def extract_keywords(self, top_n: int = 10) -> List[str]:
        """
        Extract top keywords from the transcript.
        """
        if not self.words:
            return []

        # Filter out common words (simple stop word list)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
            'now', 'here', 'there', 'then', 'once', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out',
            'off', 'over', 'under', 'again', 'further', 'get', 'got', 'going',
            'go', 'went', 'like', 'make', 'well', 'back', 'think', 'say', 'said'
        }

        filtered_words = [w for w in self.words if w not in stop_words and len(w) > 2]
        word_counts = Counter(filtered_words)

        # Get top N keywords
        top_keywords = [word for word, count in word_counts.most_common(top_n)]

        return top_keywords

    def generate_follow_up_recommendations(self, action_items: List[Dict]) -> str:
        """
        Generate follow-up recommendations based on action items and meeting content.
        """
        recommendations = []

        if not action_items:
            recommendations.append(
                "Consider defining specific action items for better accountability."
            )
        else:
            pending_count = len(action_items)
            recommendations.append(
                f"Follow up on {pending_count} action item(s) from this meeting."
            )

        # Check for keywords that suggest needs
        if any(word in self.words for word in ['decision', 'approve', 'confirm']):
            recommendations.append(
                "Send a summary email confirming all decisions made."
            )

        if any(word in self.words for word in ['deadline', 'timeline', 'schedule']):
            recommendations.append(
                "Create a timeline tracker for all deadline-sensitive tasks."
            )

        if any(word in self.words for word in ['budget', 'cost', 'resource']):
            recommendations.append(
                "Review and approve budget allocations mentioned in the meeting."
            )

        # Add generic recommendation if list is short
        if len(recommendations) < 2:
            recommendations.append(
                "Schedule a follow-up meeting to review progress on action items."
            )

        return " | ".join(recommendations)

    def analyze_complete(self) -> Dict:
        """
        Run complete analysis and return all results.
        """
        action_items = self.extract_action_items()
        summary = self.generate_summary()
        sentiment, sentiment_score = self.analyze_sentiment()
        productivity_score = self.calculate_productivity_score(len(action_items))
        keywords = self.extract_keywords()
        follow_up = self.generate_follow_up_recommendations(action_items)

        return {
            'action_items': action_items,
            'summary': summary,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'productivity_score': productivity_score,
            'keywords': keywords,
            'follow_up_recommendations': follow_up,
            'word_count': len(self.words),
            'action_items_count': len(action_items)
        }


def analyze_meeting(transcript: str, duration_minutes: int) -> Dict:
    """
    Convenience function to analyze a meeting transcript.
    """
    analyzer = MeetingAnalyzer(transcript, duration_minutes)
    return analyzer.analyze_complete()

"""
AI Interview Bot Service
ML-Driven Questioning + Scoring system for automated preliminary interviews
"""

import json
import re
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.utils import timezone
from jobs.models import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    Job, JobApplication, Skill, CandidateSkill
)
from .skills_extractor import SkillsExtractor


class InterviewBot:
    """AI-powered interview bot for automated candidate screening"""

    def __init__(self):
        self.skills_extractor = SkillsExtractor()

    def generate_interview_questions(self, job, limit=5):
        """
        Generate interview questions for a job based on its requirements

        Args:
            job: Job object
            limit: Maximum number of questions to generate

        Returns:
            List of InterviewQuestion objects
        """
        # Get job category
        category = job.category

        # Build query for relevant questions
        questions_query = InterviewQuestion.objects.filter(is_active=True)

        # Filter by category if available
        if category:
            questions_query = questions_query.filter(
                Q(category=category) | Q(category__isnull=True)
            )
        else:
            questions_query = questions_query.filter(category__isnull=True)

        # Get all relevant questions
        all_questions = list(questions_query)

        if not all_questions:
            # Return default questions if no category-specific questions exist
            return self._get_default_questions(limit)

        # Score questions based on relevance to job
        scored_questions = []
        for q in all_questions:
            relevance_score = self._calculate_question_relevance(q, job)
            scored_questions.append((q, relevance_score))

        # Sort by relevance and return top questions
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in scored_questions[:limit]]

    def _calculate_question_relevance(self, question, job):
        """
        Calculate relevance score of a question to a job

        Args:
            question: InterviewQuestion object
            job: Job object

        Returns:
            Relevance score (0-100)
        """
        score = 0

        # Category match (30 points)
        if question.category and question.category == job.category:
            score += 30
        elif not question.category:
            score += 10  # Generic question

        # Skills match (40 points)
        if question.skills_tested.exists():
            job_skills = self.skills_extractor.extract_from_job_description(
                job.requirements + ' ' + job.description
            )
            question_skills = list(question.skills_tested.values_list('name', flat=True))

            if job_skills:
                matched = len(set([s.lower() for s in job_skills]) &
                            set([s.lower() for s in question_skills]))
                score += int((matched / len(job_skills)) * 40)

        # Difficulty match with experience level (20 points)
        if job.experience_level == 'entry' and question.difficulty == 'easy':
            score += 20
        elif job.experience_level == 'mid' and question.difficulty == 'medium':
            score += 20
        elif job.experience_level in ['senior', 'executive'] and question.difficulty == 'hard':
            score += 20
        elif question.difficulty == 'medium':
            score += 10  # Medium difficulty is generally applicable

        # Question type diversity (10 points)
        # This will be handled at selection time

        return score

    def _get_default_questions(self, limit):
        """Get default/fallback interview questions"""
        defaults = [
            {
                'question_type': 'experience',
                'question': 'Tell us about your relevant work experience for this role.',
                'difficulty': 'easy',
                'expected_keywords': ['experience', 'work', 'years', 'role', 'project'],
                'max_score': 10
            },
            {
                'question_type': 'technical',
                'question': 'What technical skills do you bring to this position?',
                'difficulty': 'medium',
                'expected_keywords': ['skills', 'knowledge', 'proficient', 'expert'],
                'max_score': 10
            },
            {
                'question_type': 'behavioral',
                'question': 'Describe a challenging situation you faced at work and how you resolved it.',
                'difficulty': 'medium',
                'expected_keywords': ['challenge', 'resolved', 'solution', 'team', 'problem'],
                'max_score': 10
            },
            {
                'question_type': 'situational',
                'question': 'How would you handle a tight deadline on a critical project?',
                'difficulty': 'medium',
                'expected_keywords': ['deadline', 'prioritize', 'communicate', 'plan', 'manage'],
                'max_score': 10
            },
            {
                'question_type': 'experience',
                'question': 'Why are you interested in this position and our company?',
                'difficulty': 'easy',
                'expected_keywords': ['interested', 'company', 'role', 'grow', 'contribute'],
                'max_score': 10
            }
        ]
        return defaults[:limit]

    def score_response(self, question, answer, time_taken=None):
        """
        Score a candidate's response to an interview question using ML techniques

        Args:
            question: InterviewQuestion object or dict
            answer: Candidate's answer text
            time_taken: Time taken to answer (optional)

        Returns:
            Dictionary with score, feedback, and keywords found
        """
        if isinstance(question, dict):
            question_type = question.get('question_type', '')
            expected_keywords = question.get('expected_keywords', [])
            max_score = question.get('max_score', 10)
            question_text = question.get('question', '')
            correct_answer = question.get('correct_answer', '')
        else:
            question_type = question.question_type
            expected_keywords = question.expected_keywords
            max_score = question.max_score
            question_text = question.question
            correct_answer = question.correct_answer

        # Handle MCQ questions
        if question_type == 'mcq':
            is_correct = answer.strip().lower() == correct_answer.strip().lower()
            if is_correct:
                return {
                    'score': max_score,
                    'max_score': max_score,
                    'percentage': 100.0,
                    'feedback': 'Correct! Well done.',
                    'keywords_found': [answer]
                }
            else:
                return {
                    'score': 0,
                    'max_score': max_score,
                    'percentage': 0.0,
                    'feedback': f'Incorrect. The correct answer is: {correct_answer}',
                    'keywords_found': []
                }

        # Initialize score components for text-based questions
        score = 0
        feedback_points = []
        keywords_found = []

        # 1. Answer length check (20% of score)
        answer_words = len(answer.split())
        if answer_words < 20:
            feedback_points.append("Answer is too brief. Please provide more details.")
        elif answer_words >= 50:
            score += int(max_score * 0.2)
            feedback_points.append("Good answer length with detailed explanation.")
        else:
            score += int(max_score * 0.15)

        # 2. Keyword matching (40% of score)
        if expected_keywords:
            answer_lower = answer.lower()
            matched_keywords = []
            for keyword in expected_keywords:
                if keyword.lower() in answer_lower:
                    matched_keywords.append(keyword)
                    keywords_found.append(keyword)

            if matched_keywords:
                keyword_score = int((len(matched_keywords) / len(expected_keywords)) * max_score * 0.4)
                score += keyword_score
                feedback_points.append(f"Found relevant keywords: {', '.join(matched_keywords)}")
            else:
                feedback_points.append("Consider including more relevant terms in your answer.")

        # 3. Content quality indicators (25% of score)
        quality_indicators = [
            'because', 'therefore', 'for example', 'such as', 'specifically',
            'resulted in', 'achieved', 'implemented', 'developed', 'managed',
            'experience', 'learned', 'improved', 'successfully'
        ]

        quality_matches = sum(1 for indicator in quality_indicators
                            if indicator.lower() in answer.lower())

        if quality_matches >= 3:
            score += int(max_score * 0.25)
            feedback_points.append("Good use of explanatory language and examples.")
        elif quality_matches >= 1:
            score += int(max_score * 0.15)

        # 4. Time consideration (15% of score) - if time data available
        if time_taken is not None:
            if time_taken <= 120:  # 2 minutes
                score += int(max_score * 0.15)
                feedback_points.append("Good response time.")
            elif time_taken <= 300:  # 5 minutes
                score += int(max_score * 0.10)
            # No penalty for longer answers - quality matters more

        # Ensure score doesn't exceed max
        score = min(score, max_score)

        # Generate final feedback
        feedback = " ".join(feedback_points)

        # Determine overall assessment
        percentage = (score / max_score) * 100
        if percentage >= 80:
            feedback += " Excellent response!"
        elif percentage >= 60:
            feedback += " Good response."
        elif percentage >= 40:
            feedback += " Adequate response with room for improvement."
        else:
            feedback += " Please consider providing more detailed answers."

        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'feedback': feedback,
            'keywords_found': keywords_found
        }

    def create_interview_session(self, job, candidate):
        """
        Create a new interview session for a candidate

        Args:
            job: Job object
            candidate: User object (candidate)

        Returns:
            InterviewSession object
        """
        # Check if session already exists and is in progress
        existing = InterviewSession.objects.filter(
            job=job,
            candidate=candidate,
            status__in=['pending', 'in_progress']
        ).first()

        # Return existing in-progress session
        if existing:
            return existing

        # Delete ALL old sessions for this job-candidate pair to allow retaking
        # (We've already confirmed there's no in-progress session above)
        InterviewSession.objects.filter(
            job=job,
            candidate=candidate
        ).delete()

        # Calculate time limit based on job level
        time_limits = {
            'entry': 20,
            'mid': 30,
            'senior': 40,
            'executive': 45
        }
        time_limit = time_limits.get(job.experience_level, 30)

        # Create new session
        session = InterviewSession.objects.create(
            job=job,
            candidate=candidate,
            status='pending',
            time_limit_minutes=time_limit
        )

        return session

    def calculate_interview_score(self, session):
        """
        Calculate total interview score for a completed session

        Args:
            session: InterviewSession object

        Returns:
            Dictionary with total score and feedback
        """
        responses = session.responses.all()

        if not responses:
            return {
                'total_score': 0,
                'max_score': session.max_score,
                'percentage': 0,
                'feedback': 'No responses recorded.'
            }

        total_score = sum(r.score for r in responses)
        max_possible = sum(r.max_score for r in responses)

        # Normalize to 100 scale
        if max_possible > 0:
            percentage = (total_score / max_possible) * 100
        else:
            percentage = 0

        # Update session
        session.total_score = total_score
        session.max_score = max_possible
        session.percentage = round(percentage, 2)
        session.save()

        # Generate feedback
        if percentage >= 80:
            overall_feedback = "Excellent performance! The candidate demonstrated strong knowledge and communication skills."
        elif percentage >= 70:
            overall_feedback = "Good performance. The candidate shows solid understanding and relevant experience."
        elif percentage >= 60:
            overall_feedback = "Average performance. The candidate has basic knowledge but may need more experience."
        elif percentage >= 50:
            overall_feedback = "Below average performance. The candidate may require additional training."
        else:
            overall_feedback = "Poor performance. The candidate lacks the required skills for this position."

        # Analyze strengths and weaknesses
        strengths = []
        weaknesses = []

        for response in responses:
            if response.score >= response.max_score * 0.7:
                strengths.append(response.question.question_type)
            elif response.score < response.max_score * 0.5:
                weaknesses.append(response.question.question_type)

        if strengths:
            overall_feedback += f" Strengths: {', '.join(set(strengths))}."
        if weaknesses:
            overall_feedback += f" Areas to improve: {', '.join(set(weaknesses))}."

        return {
            'total_score': total_score,
            'max_score': max_possible,
            'percentage': round(percentage, 2),
            'feedback': overall_feedback,
            'strengths': list(set(strengths)),
            'weaknesses': list(set(weaknesses))
        }

    def get_interview_report(self, session):
        """
        Generate comprehensive interview report

        Args:
            session: InterviewSession object

        Returns:
            Dictionary with complete interview report
        """
        responses = session.responses.select_related('question').all()

        report = {
            'session': {
                'job': session.job.title,
                'company': session.job.company,
                'candidate': session.candidate.get_full_name() or session.candidate.username,
                'started_at': session.started_at,
                'completed_at': session.completed_at,
                'status': session.get_status_display(),
                'time_limit_minutes': session.time_limit_minutes
            },
            'overall_score': {
                'total': session.total_score,
                'max': session.max_score,
                'percentage': float(session.percentage),
                'grade': session.score_grade,
                'feedback': session.feedback
            },
            'responses': []
        }

        for response in responses:
            report['responses'].append({
                'question': response.question.question,
                'type': response.question.get_question_type_display(),
                'difficulty': response.question.get_difficulty_display(),
                'answer': response.answer,
                'score': response.score,
                'max_score': response.max_score,
                'percentage': round((response.score / response.max_score * 100), 2) if response.max_score > 0 else 0,
                'feedback': response.feedback,
                'keywords_found': response.keywords_found,
                'time_taken': response.time_taken_seconds
            })

        return report

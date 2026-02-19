"""
AI Matchmaking Service
Matches jobs with candidates based on skills, experience, location, and other factors
"""

from datetime import datetime, timedelta
from django.db.models import Q, Sum, Count
from django.utils import timezone
from accounts.models import UserProfile
from jobs.models import Job, JobApplication, CandidateSkill
from .skills_extractor import SkillsExtractor


class JobMatchmaker:
    """AI-powered job-candidate matching engine"""

    def __init__(self):
        self.skills_extractor = SkillsExtractor()

    def find_candidates_for_job(self, job, limit=10, min_score=30):
        """
        Find top candidates for a job

        Args:
            job: Job object to find candidates for
            limit: Maximum number of candidates to return
            min_score: Minimum match score threshold (0-100)

        Returns:
            List of dictionaries with candidate info and match scores
        """
        # Get all job seeker profiles
        candidates = UserProfile.objects.filter(
            user_type='job_seeker'
        ).select_related('user').prefetch_related(
            'candidate_skills__skill',
            'work_experiences',
            'educations'
        )

        scored_candidates = []

        for profile in candidates:
            # Calculate match score
            score_data = self._calculate_match_score(job, profile)

            if score_data['total_score'] >= min_score:
                scored_candidates.append({
                    'user': profile.user,
                    'profile': profile,
                    'score': score_data['total_score'],
                    'reasons': score_data['reasons'],
                    'breakdown': score_data['breakdown']
                })

        # Sort by score and return top candidates
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates[:limit]

    def generate_recommendations_for_user(self, user, limit=5, min_score=40):
        """
        Generate job recommendations for a job seeker

        Args:
            user: User object to get recommendations for
            limit: Maximum number of recommendations to return
            min_score: Minimum match score threshold (0-100)

        Returns:
            List of dictionaries with job info and match scores
        """
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return []

        # Only generate recommendations for job seekers
        if profile.user_type != 'job_seeker':
            return []

        # Get active jobs
        jobs = Job.objects.filter(status='active').select_related('category', 'created_by')

        recommendations = []

        for job in jobs:
            # Skip if already applied (JobApplication uses email, not user)
            if JobApplication.objects.filter(email=user.email, job=job).exists():
                continue

            # Skip if already saved
            from jobs.models import SavedJob
            if SavedJob.objects.filter(user=user, job=job).exists():
                # Lower score for already saved jobs
                score_modifier = -5
            else:
                score_modifier = 0

            # Calculate recommendation score
            score_data = self._calculate_match_score(job, profile)

            adjusted_score = max(0, score_data['total_score'] + score_modifier)

            if adjusted_score >= min_score:
                recommendations.append({
                    'job': job,
                    'score': adjusted_score,
                    'reason': score_data['reasons'],
                    'breakdown': score_data['breakdown']
                })

        # Sort and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]

    def _calculate_match_score(self, job, candidate_profile):
        """
        Calculate comprehensive match score between job and candidate

        Returns:
            Dictionary with total_score, reasons, and breakdown
        """
        score = 0
        breakdown = {
            'skills': 0,
            'experience': 0,
            'location': 0,
            'education': 0,
            'activity': 0
        }
        reasons = []

        # 1. Skills match (40% weight)
        candidate_skills = list(candidate_profile.candidate_skills.values_list('skill__name', flat=True))
        required_skills = self.skills_extractor.extract_from_job_description(
            job.requirements + ' ' + job.description
        )

        if required_skills:
            skills_score = self.skills_extractor.calculate_skill_match_score(
                candidate_skills, required_skills
            )
            breakdown['skills'] = int(skills_score * 0.4)
            score += breakdown['skills']

            matched_skills = self.skills_extractor.get_matched_skills(candidate_skills, required_skills)
            if matched_skills:
                reasons.append(f"Has {len(matched_skills)} required skills: {', '.join(matched_skills[:5])}")
        else:
            # Give partial points if no skills specified
            breakdown['skills'] = int(40 * 0.5)
            score += breakdown['skills']

        # 2. Experience level match (20% weight)
        total_exp_years = self._calculate_total_experience(candidate_profile)
        breakdown['experience'] = self._calculate_experience_score(job, total_exp_years)
        score += breakdown['experience']

        if total_exp_years > 0:
            reasons.append(f"Has {total_exp_years} years of experience")
        if job.experience_level == 'entry' and total_exp_years < 2:
            reasons.append("Experience level matches entry-level position")
        elif job.experience_level == 'mid' and 2 <= total_exp_years < 5:
            reasons.append("Experience level matches mid-level position")
        elif job.experience_level == 'senior' and total_exp_years >= 5:
            reasons.append("Experience level matches senior position")

        # 3. Location match (15% weight)
        if candidate_profile.location and job.location:
            location_match = self._calculate_location_score(candidate_profile.location, job.location)
            breakdown['location'] = location_match
            score += location_match

            if location_match > 0:
                reasons.append(f"Location match: {candidate_profile.location}")

        # 4. Education match (15% weight)
        education_score = self._calculate_education_score(job, candidate_profile)
        breakdown['education'] = education_score
        score += education_score

        if candidate_profile.educations.exists():
            latest_edu = candidate_profile.educations.first()
            reasons.append(f"Education: {latest_edu.get_degree_type_display()} in {latest_edu.field_of_study}")

        # 5. Application activity (10% weight)
        activity_score = self._calculate_activity_score(job, candidate_profile.user)
        breakdown['activity'] = activity_score
        score += activity_score

        return {
            'total_score': min(100, score),  # Cap at 100
            'reasons': reasons,
            'breakdown': breakdown
        }

    def _calculate_total_experience(self, profile):
        """Calculate total years of work experience"""
        experiences = profile.work_experiences.filter(is_current=False)

        total_days = 0
        for exp in experiences:
            if exp.start_date and exp.end_date:
                delta = exp.end_date - exp.start_date
                total_days += delta.days

        # Add current position if exists
        current_exp = profile.work_experiences.filter(is_current=True).first()
        if current_exp and current_exp.start_date:
            delta = datetime.now().date() - current_exp.start_date
            total_days += delta.days

        return int(total_days / 365.25)  # Convert to years

    def _calculate_experience_score(self, job, total_exp_years):
        """Calculate experience match score (max 20)"""
        score = 0

        if job.experience_level == 'entry':
            if total_exp_years < 2:
                score = 20
            elif total_exp_years < 4:
                score = 15
            else:
                score = 10  # Overqualified but still good
        elif job.experience_level == 'mid':
            if 2 <= total_exp_years < 5:
                score = 20
            elif 1 <= total_exp_years < 2 or 5 <= total_exp_years < 7:
                score = 15
            elif total_exp_years >= 1:
                score = 10
        elif job.experience_level == 'senior':
            if total_exp_years >= 5:
                score = 20
            elif total_exp_years >= 3:
                score = 15
            elif total_exp_years >= 1:
                score = 10
        elif job.experience_level == 'executive':
            if total_exp_years >= 10:
                score = 20
            elif total_exp_years >= 7:
                score = 15
            elif total_exp_years >= 5:
                score = 10

        return score

    def _calculate_location_score(self, candidate_location, job_location):
        """Calculate location match score (max 15)"""
        candidate_loc = candidate_location.lower().strip()
        job_loc = job_location.lower().strip()

        # Exact match
        if candidate_loc == job_loc:
            return 15

        # Contains match
        if candidate_loc in job_loc or job_loc in candidate_loc:
            return 12

        # Remote jobs get automatic high score
        if 'remote' in job_loc or 'anywhere' in job_loc or 'worldwide' in job_loc:
            return 15

        # Same country/state (partial match)
        candidate_parts = candidate_loc.split(',')
        job_parts = job_loc.split(',')

        if len(candidate_parts) > 1 and len(job_parts) > 1:
            # Check if country/state matches
            if candidate_parts[-1].strip() == job_parts[-1].strip():
                return 8

        return 0

    def _calculate_education_score(self, job, profile):
        """Calculate education match score (max 15)"""
        if not profile.educations.exists():
            return 5  # Basic points for having any profile

        score = 0
        educations = profile.educations.all()

        # Check for higher education
        for edu in educations:
            if edu.degree_type in ['master', 'phd']:
                score += 10
            elif edu.degree_type == 'bachelor':
                score += 7
            elif edu.degree_type in ['diploma', 'certificate']:
                score += 5

        # Field relevance (basic check)
        job_keywords = job.description.lower() + ' ' + job.requirements.lower()
        for edu in educations:
            if edu.field_of_study.lower() in job_keywords:
                score += 3
                break

        return min(15, score)

    def _calculate_activity_score(self, job, user):
        """Calculate application activity score (max 10)"""
        # Check for past applications to similar jobs (JobApplication uses email, not user)
        similar_jobs = Job.objects.filter(
            category=job.category
        ).exclude(id=job.id)

        past_applications = JobApplication.objects.filter(
            email=user.email,
            job__in=similar_jobs
        ).count()

        # Award points for being active in the category
        activity_score = min(past_applications * 3, 10)
        return activity_score

"""
Skills Extraction Service
Extracts skills from resumes and job descriptions using pattern matching and keyword analysis
"""

import re
from collections import Counter
from jobs.models import Skill


class SkillsExtractor:
    """Extract and match skills from text"""

    def __init__(self):
        self.skills_cache = None

    def _load_skills_database(self):
        """Load skills from database (with caching)"""
        if self.skills_cache is None:
            self.skills_cache = list(Skill.objects.values_list('name', flat=True))
        return self.skills_cache

    def extract_from_text(self, text, case_sensitive=False):
        """
        Extract skills from text using pattern matching

        Args:
            text: The text to extract skills from
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            Counter object with skills and their occurrence counts
        """
        if not text:
            return Counter()

        skills_db = self._load_skills_database()
        extracted_skills = Counter()

        for skill in skills_db:
            # Create regex pattern for whole word matching
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = r'\b' + re.escape(skill) + r'\b'

            matches = re.findall(pattern, text, flags)
            if matches:
                extracted_skills[skill] += len(matches)

        return extracted_skills

    def extract_from_resume(self, resume_text):
        """
        Extract skills from resume text

        Args:
            resume_text: The full text of the resume

        Returns:
            List of unique skills found in the resume
        """
        if not resume_text:
            return []

        skills_counter = self.extract_from_text(resume_text)
        return list(skills_counter.keys())

    def extract_from_job_description(self, job_description):
        """
        Extract required skills from job description

        Args:
            job_description: The job description/requirements text

        Returns:
            List of unique skills found in the job description
        """
        if not job_description:
            return []

        skills_counter = self.extract_from_text(job_description)
        return list(skills_counter.keys())

    def calculate_skill_match_score(self, candidate_skills, job_required_skills):
        """
        Calculate skill match percentage

        Args:
            candidate_skills: List of candidate's skills
            job_required_skills: List of required job skills

        Returns:
            Integer score from 0-100
        """
        if not job_required_skills:
            return 0

        candidate_set = set([s.lower() for s in candidate_skills])
        required_set = set([s.lower() for s in job_required_skills])

        # Find matched skills (case-insensitive)
        matched = len(candidate_set & required_set)
        total = len(required_set)

        if total == 0:
            return 0

        return int((matched / total) * 100)

    def get_missing_skills(self, candidate_skills, job_required_skills):
        """
        Get skills that the candidate is missing

        Args:
            candidate_skills: List of candidate's skills
            job_required_skills: List of required job skills

        Returns:
            List of missing skills
        """
        if not job_required_skills:
            return []

        candidate_set = set([s.lower() for s in candidate_skills])
        required_set = set([s.lower() for s in job_required_skills])

        missing = required_set - candidate_set
        return list(missing)

    def get_matched_skills(self, candidate_skills, job_required_skills):
        """
        Get skills that match between candidate and job

        Args:
            candidate_skills: List of candidate's skills
            job_required_skills: List of required job skills

        Returns:
            List of matched skills
        """
        if not candidate_skills or not job_required_skills:
            return []

        candidate_set = set([s.lower() for s in candidate_skills])
        required_set = set([s.lower() for s in job_required_skills])

        matched = candidate_set & required_set
        return list(matched)

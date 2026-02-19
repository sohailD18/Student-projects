"""
Seed Data Script for GovExamPortal

Run this script to populate the database with sample exam data:
python manage.py shell < seed_data.py

OR manually:
python manage.py shell
>>> exec(open('seed_data.py').read())
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GovExamPortal.settings')
django.setup()

from datetime import date, timedelta
from exams.models import Exam


def clear_exams():
    """Clear all existing exams"""
    Exam.objects.all().delete()
    print("Cleared all existing exams.")


def create_sample_exams():
    """Create sample government examination data"""

    exams_data = [
        # UPSC Exams
        {
            'title': 'Civil Services Examination (CSE) 2025',
            'exam_type': 'UPSC',
            'official_link': 'https://www.upsc.gov.in/examinations/Civil%20Services%20(Pre)%20Examination',
            'description': 'UPSC Civil Services Examination for recruitment to various Civil Services of the Government of India, including IAS, IFS, IPS, and other Group A and B services.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree from any recognized university. Candidates who are in their final year of degree can also apply.',
            'age_limit_min': 21,
            'age_limit_max': 32,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: General Studies Paper I & II (CSAT). Mains: 9 Papers including Essay, GS Papers I-IV, Optional Subject (2 papers), and Indian Languages & English.',
            'application_start_date': date(2025, 2, 15),
            'application_end_date': date(2025, 3, 15),
            'exam_date': date(2025, 5, 26),
        },
        {
            'title': 'Indian Forest Service Examination (IFoS) 2025',
            'exam_type': 'UPSC',
            'official_link': 'https://www.upsc.gov.in/examinations/Indian%20Forest%20Service',
            'description': 'Examination for recruitment to Indian Forest Service Officers. The examination consists of written test and interview.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree with at least one of the subjects: Animal Husbandry, Botany, Chemistry, Geology, Mathematics, Physics, Zoology, or a Bachelor\'s degree in Agriculture/Forestry/Engineering.',
            'age_limit_min': 21,
            'age_limit_max': 32,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: Civil Services (Prelims) Examination. Mains: General English, General Knowledge, and two optional subjects from the prescribed list.',
            'application_start_date': date(2025, 2, 10),
            'application_end_date': date(2025, 3, 10),
            'exam_date': date(2025, 5, 26),
        },

        # SSC Exams
        {
            'title': 'SSC Combined Graduate Level (CGL) 2025',
            'exam_type': 'SSC',
            'official_link': 'https://ssc.nic.in/portal/schemeexamination',
            'description': 'SSC CGL examination for recruitment to various Group B and Group C posts in Ministries, Departments, and Organizations of the Government of India.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree from a recognized university. For certain posts, specific educational qualifications are required.',
            'age_limit_min': 18,
            'age_limit_max': 30,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Tier I: General Intelligence, General Awareness, Quantitative Aptitude, English Comprehension. Tier II: Quantitative Abilities, English Language, Statistics, General Studies.',
            'application_start_date': date(2025, 3, 1),
            'application_end_date': date(2025, 3, 31),
            'exam_date': date(2025, 6, 15),
        },
        {
            'title': 'SSC Combined Higher Secondary Level (CHSL) 2025',
            'exam_type': 'SSC',
            'official_link': 'https://ssc.nic.in/portal/schemeexamination',
            'description': 'SSC CHSL examination for recruitment to Lower Division Clerk, Postal Assistant, Sorting Assistant, and Data Entry Operator posts.',
            'eligibility_criteria': 'Candidate must have passed 12th Standard or equivalent from a recognized Board or University.',
            'age_limit_min': 18,
            'age_limit_max': 27,
            'educational_qualification': '12TH',
            'syllabus_text': 'Tier I: General Intelligence, General Awareness, Quantitative Aptitude, English Language. Tier II: English Language & Comprehension. Skill Test: Typing/Data Entry.',
            'application_start_date': date(2025, 4, 1),
            'application_end_date': date(2025, 4, 30),
            'exam_date': date(2025, 7, 10),
        },

        # Banking Exams
        {
            'title': 'IBPS Probationary Officer (PO) XV',
            'exam_type': 'BANKING',
            'official_link': 'https://ibps.in/cwe-probationary-officers-management-trainees/',
            'description': 'IBPS PO/MT recruitment for participating banks. This is a common written examination for the post of Probationary Officer/Management Trainee.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree in any discipline from a recognized university. Final year students can also apply provisionally.',
            'age_limit_min': 20,
            'age_limit_max': 30,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: English Language, Quantitative Aptitude, Reasoning Ability. Mains: Reasoning & Computer Aptitude, General/Economy/Banking Awareness, English Language, Data Analysis & Interpretation.',
            'application_start_date': date(2025, 3, 15),
            'application_end_date': date(2025, 4, 15),
            'exam_date': date(2025, 7, 5),
        },
        {
            'title': 'SBI Clerk 2025',
            'exam_type': 'BANKING',
            'official_link': 'https://sbi.co.in/careers',
            'description': 'State Bank of India Junior Associate (Customer Support & Sales) examination for recruitment of Clerical cadre in SBI branches.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree in any discipline from a recognized university. Knowledge of local language is preferred.',
            'age_limit_min': 20,
            'age_limit_max': 28,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: English Language, Numerical Ability, Reasoning Ability. Mains: General/Financial Awareness, General English, Quantitative Aptitude, Reasoning Ability & Computer Aptitude.',
            'application_start_date': date(2025, 4, 5),
            'application_end_date': date(2025, 4, 25),
            'exam_date': date(2025, 7, 20),
        },

        # Railways Exams
        {
            'title': 'RRB Non-Technical Popular Categories (NTPC) 2025',
            'exam_type': 'RAILWAYS',
            'official_link': 'https://www.rrbcdg.gov.in/',
            'description': 'Railway Recruitment Board NTPC examination for posts like Clerk, Assistant, Station Master, Goods Guard, etc. in Indian Railways.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree from a recognized university. For certain posts, 12th pass with minimum 50% marks is also eligible.',
            'age_limit_min': 18,
            'age_limit_max': 33,
            'educational_qualification': '12TH',
            'syllabus_text': 'CBT 1: General Awareness, Mathematics, General Intelligence & Reasoning. CBT 2: General Awareness, Mathematics & Reasoning, relevant trade knowledge.',
            'application_start_date': date(2025, 3, 20),
            'application_end_date': date(2025, 4, 20),
            'exam_date': date(2025, 6, 10),
        },
        {
            'title': 'RRB Level 1 (Group D) 2025',
            'exam_type': 'RAILWAYS',
            'official_link': 'https://www.rrbcdg.gov.in/',
            'description': 'RRB Group D examination for various Level 1 posts like Track Maintainer, Helper, Assistant Pointsman, etc. in Indian Railways.',
            'eligibility_criteria': 'Candidate must have passed 10th standard from a recognized board. ITI in relevant trade or National Apprenticeship Certificate (NAC) granted by NCVT is also acceptable.',
            'age_limit_min': 18,
            'age_limit_max': 33,
            'educational_qualification': '10TH',
            'syllabus_text': 'CBT: General Science, Mathematics, General Intelligence & Reasoning, General Awareness & Current Affairs.',
            'application_start_date': date(2025, 4, 10),
            'application_end_date': date(2025, 5, 10),
            'exam_date': date(2025, 7, 25),
        },

        # State PSC Exams
        {
            'title': 'Uttar Pradesh Public Service Commission (UPPSC) 2025',
            'exam_type': 'STATE_PSC',
            'official_link': 'http://uppsc.up.nic.in/',
            'description': 'UPPSC Combined State/Upper Subordinate Services Examination for recruitment to various administrative posts in Uttar Pradesh government.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree from a recognized university. Candidates must be domicile of Uttar Pradesh.',
            'age_limit_min': 21,
            'age_limit_max': 40,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: General Studies Paper I & II. Mains: General Hindi, Essay, General Studies I-III, Optional Subject, General Studies IV (Ethics), Interview.',
            'application_start_date': date(2025, 2, 20),
            'application_end_date': date(2025, 3, 20),
            'exam_date': date(2025, 5, 15),
        },
        {
            'title': 'Maharashtra Public Service Commission (MPSC) 2025',
            'exam_type': 'STATE_PSC',
            'official_link': 'https://mpsc.gov.in/',
            'description': 'MPSC State Services Examination for recruitment to Class I and Class II posts in Maharashtra government administration.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree from a recognized university. Knowledge of Marathi language is required.',
            'age_limit_min': 18,
            'age_limit_max': 38,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'Preliminary: General Studies, CSAT. Mains: Marathi, English, General Studies I-IV, Optional Subject papers, Interview.',
            'application_start_date': date(2025, 3, 10),
            'application_end_date': date(2025, 4, 10),
            'exam_date': date(2025, 6, 5),
        },

        # Defence Exams
        {
            'title': 'National Defence Academy (NDA) II 2025',
            'exam_type': 'DEFENCE',
            'official_link': 'https://www.upsc.gov.in/examinations/National%20Defence%20Academy',
            'description': 'UPSC NDA examination for admission to Army, Navy, and Air Force wings of National Defence Academy and Indian Naval Academy Course.',
            'eligibility_criteria': 'For Army: 12th pass. For Air Force & Navy: 12th pass with Physics, Chemistry, and Mathematics. Only unmarried male candidates can apply.',
            'age_limit_min': 16,
            'age_limit_max': 19,
            'educational_qualification': '12TH',
            'syllabus_text': 'Mathematics (300 marks): Algebra, Calculus, Trigonometry, etc. General Ability Test (600 marks): English, General Knowledge (Physics, Chemistry, General Science, History, Geography, Current Events).',
            'application_start_date': date(2025, 5, 15),
            'application_end_date': date(2025, 6, 10),
            'exam_date': date(2025, 8, 31),
        },
        {
            'title': 'AFCAT 2 2025 - Air Force Common Admission Test',
            'exam_type': 'DEFENCE',
            'official_link': 'https://afcat.cdac.in/',
            'description': 'AFCAT for recruitment to Flying Branch, Ground Duty (Technical) and Ground Duty (Non-Technical) branches of Indian Air Force.',
            'eligibility_criteria': 'Candidate must hold a Bachelor\'s degree with minimum 60% marks. For Technical branches, B.E./B.Tech degree is required. Both men and women can apply.',
            'age_limit_min': 20,
            'age_limit_max': 26,
            'educational_qualification': 'Graduate',
            'syllabus_text': 'General Awareness: History, Geography, Sports, Current Affairs, etc. Verbal Ability: English language, error detection, synonyms, antonyms. Numerical Ability, Reasoning and Military Aptitude.',
            'application_start_date': date(2025, 5, 1),
            'application_end_date': date(2025, 5, 31),
            'exam_date': date(2025, 7, 20),
        },
    ]

    # Create exams
    created_count = 0
    for exam_data in exams_data:
        exam, created = Exam.objects.get_or_create(
            title=exam_data['title'],
            defaults=exam_data
        )
        if created:
            created_count += 1
            print(f"Created: {exam.title}")
        else:
            print(f"Already exists: {exam.title}")

    print(f"\nTotal exams created: {created_count}")
    print(f"Total exams in database: {Exam.objects.count()}")


def main():
    """Main function to run the seed data script"""
    print("=" * 60)
    print("GovExamPortal - Seed Data Script")
    print("=" * 60)

    # Ask user if they want to clear existing data
    response = input("\nDo you want to clear existing exam data? (yes/no): ").strip().lower()

    if response == 'yes' or response == 'y':
        clear_exams()

    print("\nCreating sample examination data...")
    create_sample_exams()

    print("\n" + "=" * 60)
    print("Seed data script completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()

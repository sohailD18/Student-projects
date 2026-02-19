from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import LegalDocument, AnalysisReport
from django.utils import timezone
from datetime import datetime, timedelta
import os


class Command(BaseCommand):
    help = 'Load demo data for LexiGuard application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Loading demo data...'))

        # Clear existing data
        LegalDocument.objects.all().delete()
        self.stdout.write('Cleared existing data')

        # Sample documents with demo content
        demo_documents = [
            {
                'title': 'Employment Agreement 2026',
                'filename': 'employment_agreement_2026.txt',
                'content': '''EMPLOYMENT AGREEMENT

This Employment Agreement is entered into as of January 15, 2026, between ABC Corporation (Employer) and John Doe (Employee).

1. TERMS OF EMPLOYMENT
The Employee shall serve as Senior Software Engineer. The employment shall commence on February 1, 2026.

2. COMPENSATION
The Employee shall receive an annual base salary of $95,000, payable in accordance with the Employer's standard payroll practices.

3. TERMINATION
Either party may terminate this agreement with 30 days written notice. The Employer reserves the right to terminate without cause upon payment of severance.

4. CONFIDENTIALITY
The Employee agrees to maintain the confidentiality of all proprietary information, trade secrets, and client data during and after employment.

5. INTELLECTUAL PROPERTY
All work product created by the Employee during employment shall be the exclusive property of the Employer.

6. NON-COMPETE
The Employee agrees not to work for competitors for a period of 12 months following termination.

7. LIABILITY
The Employee shall be liable for any intentional misconduct or gross negligence.

8. DISPUTE RESOLUTION
Any disputes arising from this agreement shall be resolved through binding arbitration.

9. GOVERNING LAW
This agreement shall be governed by the laws of the State of California.

10. NOTICES
All notices shall be delivered in writing to the addresses specified herein.
''',
                'delay_days': 5
            },
            {
                'title': 'Service Contract - Web Development',
                'filename': 'service_contract_web.txt',
                'content': '''WEB DEVELOPMENT SERVICES CONTRACT

This Services Agreement is made between TechSolutions Inc. and Client XYZ dated January 10, 2026.

1. SCOPE OF SERVICES
The Service Provider shall develop a custom e-commerce website including frontend, backend, and payment integration.

2. PAYMENT TERMS
Total project cost: $25,000. Payment schedule: 50% upfront, 50% upon completion.

3. INDEMNIFICATION
The Service Provider shall indemnify and hold harmless the Client from any claims arising from intellectual property infringement.

4. TERMINATION
Either party may terminate this agreement upon 15 days written notice.

5. CONFIDENTIALITY
Both parties agree to keep all project information confidential.

6. GOVERNING LAW
This contract is governed by the laws of New York.

7. LIABILITY
The Service Provider's liability shall not exceed the total amount paid under this agreement.

8. ASSIGNMENT
Neither party may assign this agreement without written consent.
''',
                'delay_days': 10
            },
            {
                'title': 'Non-Disclosure Agreement',
                'filename': 'nda_agreement.txt',
                'content': '''NON-DISCLOSURE AGREEMENT

This NDA is entered into on January 5, 2026, between StartupCo and Partner Firm.

1. CONFIDENTIAL INFORMATION
All technical data, business plans, and financial information shared between parties shall be considered confidential.

2. OBLIGATIONS
The receiving party shall maintain confidentiality and shall not disclose information to third parties.

3. TERM
This agreement shall remain in effect for a period of 3 years from the date of execution.

4. GOVERNING LAW
This agreement is governed by Delaware law.

5. DISPUTE RESOLUTION
Any disputes shall be resolved through mediation before litigation.
''',
                'delay_days': 3
            },
            {
                'title': 'Lease Agreement - Office Space',
                'filename': 'lease_agreement.txt',
                'content': '''COMMERCIAL LEASE AGREEMENT

This Lease is made on January 1, 2026, between Landlord Properties LLC and Tenant Business Inc.

1. PREMISES
The Landlord agrees to lease 2,500 square feet of office space located at 123 Business Ave.

2. TERM
The lease term shall be 36 months commencing February 1, 2026.

3. PAYMENT TERMS
Monthly rent: $4,500. Due on the 1st of each month.

4. TERMINATION
Either party may terminate with 60 days notice for cause.

5. LIABILITY
The Tenant shall maintain liability insurance with minimum coverage of $1,000,000.

6. NOTICES
All notices must be sent via certified mail.

7. AMENDMENT
Any changes to this agreement must be made in writing and signed by both parties.
''',
                'delay_days': 15
            },
            {
                'title': 'Independent Contractor Agreement',
                'filename': 'contractor_agreement.txt',
                'content': '''INDEPENDENT CONTRACTOR AGREEMENT

This agreement is dated January 20, 2026, between Company ABC and Consultant Jane Smith.

1. SERVICES
The Consultant shall provide marketing consulting services as requested.

2. COMPENSATION
The Consultant shall be paid $75 per hour for all services rendered.

3. INTELLECTUAL PROPERTY
All deliverables shall become the exclusive property of the Company.

4. CONFIDENTIALITY
The Consultant shall maintain confidentiality of all client information.

5. TERMINATION
Either party may terminate this agreement at any time with 7 days notice.

6. GOVERNING LAW
This agreement shall be governed by Texas law.
''',
                'delay_days': 1
            }
        ]

        # Create documents
        for i, demo in enumerate(demo_documents, 1):
            # Create a temp file (without media/ prefix - Django adds it automatically)
            relative_path = f'legal_documents/{demo["filename"]}'
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(demo['content'])

            # Create document record
            created_date = timezone.now() - timedelta(days=demo['delay_days'])
            document = LegalDocument.objects.create(
                title=demo['title'],
                uploaded_file=relative_path,
                created_at=created_date
            )

            # Create analysis report
            from core.utils import analyze_document_text
            analysis = analyze_document_text(demo['content'])

            AnalysisReport.objects.create(
                document=document,
                risk_level=analysis['risk_level'],
                summary=analysis['summary'],
                is_compliant=(analysis['risk_level'] == 'LOW')
            )

            self.stdout.write(f'  [OK] Created: {demo["title"]}')

        self.stdout.write(self.style.SUCCESS(f'\n[OK] Successfully created {len(demo_documents)} demo documents'))
        self.stdout.write(self.style.SUCCESS('[OK] Analysis reports generated for all documents'))
        self.stdout.write('\nYou can now visit http://127.0.0.1:8000/ to see the demo data!')

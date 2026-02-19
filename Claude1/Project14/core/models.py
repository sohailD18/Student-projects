from django.db import models


class LegalDocument(models.Model):
    """Model for storing uploaded legal documents."""
    title = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='legal_documents/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AnalysisReport(models.Model):
    """Model for storing analysis results of legal documents."""
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
    ]

    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name='analysis_reports'
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default='LOW'
    )
    summary = models.TextField()
    is_compliant = models.BooleanField(default=False)

    class Meta:
        ordering = ['-document__created_at']

    def __str__(self):
        return f"Analysis for {self.document.title} - {self.risk_level}"

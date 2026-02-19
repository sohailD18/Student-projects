"""
Database models for AgriSense application.
"""
from django.db import models


class SoilData(models.Model):
    """
    Model to store soil analysis data and recommendations.
    """
    nitrogen = models.IntegerField(help_text="Nitrogen level (N)")
    phosphorus = models.IntegerField(help_text="Phosphorus level (P)")
    potassium = models.IntegerField(help_text="Potassium level (K)")
    ph_level = models.FloatField(help_text="Soil pH level")
    moisture = models.FloatField(help_text="Soil moisture percentage")
    recommended_crop = models.CharField(max_length=100, help_text="AI recommended crop")
    fertilizer_suggestion = models.TextField(help_text="Fertilizer recommendations")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Analysis timestamp")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Soil Data"
        verbose_name_plural = "Soil Data"

    def __str__(self):
        return f"Soil Analysis {self.id} - {self.recommended_crop}"


class ContactMessage(models.Model):
    """
    Model to store contact form submissions.
    """
    name = models.CharField(max_length=100, help_text="Contact name")
    email = models.EmailField(help_text="Contact email address")
    message = models.TextField(help_text="Contact message")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Message timestamp")
    is_read = models.BooleanField(default=False, help_text="Whether message has been read")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

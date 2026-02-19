"""
Database Models for Worker Safety Monitoring System
Stores safety incidents, violations, and system metrics.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import os


def snapshot_upload_path(instance, filename):
    """
    Generate dynamic upload path for snapshots.
    Format: media/snapshots/YYYY-MM-DD/filename
    """
    from django.utils import timezone
    date_str = timezone.now().strftime('%Y-%m-%d')
    return os.path.join('snapshots', date_str, filename)


class SafetyIncident(models.Model):
    """
    Model to store safety violations and hazard detections.
    Each record represents a detected safety violation.
    """
    HAZARD_TYPES = [
        ('NO_HELMET', 'No Helmet'),
        ('NO_VEST', 'No Safety Vest'),
        ('RESTRICTED_ZONE', 'Restricted Zone Intrusion'),
        ('NO_PPE', 'Missing PPE'),
        ('MULTIPLE_VIOLATIONS', 'Multiple Violations'),
    ]

    # Unique identifier for each incident
    incident_id = models.AutoField(primary_key=True)

    # Timestamp when the hazard was detected
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the violation was detected"
    )

    # Camera or video source identifier
    camera_id = models.CharField(
        max_length=50,
        default='CAM-01',
        help_text="Identifier for the camera that detected the incident"
    )

    # Type of hazard detected
    hazard_type = models.CharField(
        max_length=50,
        choices=HAZARD_TYPES,
        help_text="Type of safety violation detected"
    )

    # AI confidence score (0.0 to 1.0)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI detection confidence score (0-100%)"
    )

    # Snapshot image of the violation
    image_path = models.ImageField(
        upload_to=snapshot_upload_path,
        null=True,
        blank=True,
        help_text="Snapshot image captured at the time of violation"
    )

    # Whether the incident has been reviewed/resolved
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether the incident has been reviewed and resolved"
    )

    # Additional notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments about the incident"
    )

    # Detection details (JSON stored as text)
    detection_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional detection metadata (bounding boxes, etc.)"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Safety Incident"
        verbose_name_plural = "Safety Incidents"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['hazard_type']),
            models.Index(fields=['is_resolved']),
        ]

    def __str__(self):
        """String representation of the incident."""
        return f"{self.hazard_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def confidence_percentage(self):
        """Return confidence as a percentage."""
        return round(self.confidence_score * 100, 2)


class SystemMetrics(models.Model):
    """
    Model to store daily system metrics and statistics.
    Updated periodically to track system performance.
    """
    date = models.DateField(unique=True, db_index=True)
    workers_detected = models.IntegerField(default=0)
    total_violations = models.IntegerField(default=0)
    safety_score = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    active_cameras = models.IntegerField(default=1)
    monitoring_hours = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']
        verbose_name = "System Metric"
        verbose_name_plural = "System Metrics"

    def __str__(self):
        return f"Metrics for {self.date}"


class RestrictedZone(models.Model):
    """
    Model to define restricted zones within the monitored area.
    Zones are defined by coordinate boundaries.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the restricted zone"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of why this zone is restricted"
    )
    # Coordinates for rectangular zone (x1, y1, x2, y2)
    x1 = models.IntegerField(help_text="Top-left X coordinate")
    y1 = models.IntegerField(help_text="Top-left Y coordinate")
    x2 = models.IntegerField(help_text="Bottom-right X coordinate")
    y2 = models.IntegerField(help_text="Bottom-right Y coordinate")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Restricted Zone"
        verbose_name_plural = "Restricted Zones"

    def __str__(self):
        return self.name

    def contains_point(self, x, y):
        """Check if a point (x, y) is within this zone."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


class CameraConfig(models.Model):
    """
    Model to store camera configurations and sources.
    Supports webcams, IP cameras, and video files.
    """
    CAMERA_TYPES = [
        ('WEBCAM', 'Webcam'),
        ('IP_CAMERA', 'IP Camera'),
        ('VIDEO_FILE', 'Video File'),
        ('RTSP_STREAM', 'RTSP Stream'),
    ]

    camera_id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Unique camera identifier"
    )
    name = models.CharField(max_length=100)
    camera_type = models.CharField(
        max_length=20,
        choices=CAMERA_TYPES,
        default='WEBCAM'
    )
    source_path = models.CharField(
        max_length=255,
        help_text="Camera index (for webcam) or URL/path (for IP camera/video file)"
    )
    is_active = models.BooleanField(default=True)
    resolution_width = models.IntegerField(default=640)
    resolution_height = models.IntegerField(default=480)
    fps = models.IntegerField(default=30)

    class Meta:
        verbose_name = "Camera Configuration"
        verbose_name_plural = "Camera Configurations"

    def __str__(self):
        return f"{self.name} ({self.camera_id})"

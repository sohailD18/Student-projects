"""
Views for Worker Safety Monitoring System
Handles dashboard, video streaming, and incident logging.
"""

import cv2
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache
from pathlib import Path

from .models import SafetyIncident, SystemMetrics, RestrictedZone, CameraConfig
from .detection import SafetyDetector, VideoStream, draw_overlay_info

logger = logging.getLogger(__name__)


# Global variables for video streaming (for demo purposes)
# In production, use proper threading/async
global_stream = None
global_detector = None


def initialize_detection_system():
    """Initialize the global detector and video stream."""
    global global_detector, global_stream

    if global_detector is None:
        global_detector = SafetyDetector(confidence_threshold=0.5)
        logger.info("Safety detector initialized")

    if global_stream is None:
        global_stream = VideoStream(source=0)
        if global_stream.start():
            logger.info("Video stream started")


def dashboard(request):
    """
    Main dashboard view.
    Displays live feed, statistics, and recent incidents.
    """
    # Get current statistics
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

    # Query incidents
    total_incidents = SafetyIncident.objects.count()
    today_incidents = SafetyIncident.objects.filter(
        timestamp__gte=today_start
    ).count()

    unresolved_incidents = SafetyIncident.objects.filter(
        is_resolved=False
    ).count()

    # Get recent incidents (last 10)
    recent_incidents = SafetyIncident.objects.filter(
        timestamp__gte=today_start
    ).order_by('-timestamp')[:10]

    # Calculate safety score (simple formula)
    workers_detected_today = SystemMetrics.objects.filter(date=today).first()
    if workers_detected_today:
        safety_score = workers_detected_today.safety_score
    else:
        # Default safety score
        safety_score = 100.0 - (today_incidents * 5)
        safety_score = max(0, safety_score)

    context = {
        'page_title': 'Worker Safety Monitoring Dashboard',
        'total_incidents': total_incidents,
        'today_incidents': today_incidents,
        'unresolved_incidents': unresolved_incidents,
        'safety_score': round(safety_score, 1),
        'recent_incidents': recent_incidents,
        'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    return render(request, 'monitoring/dashboard.html', context)


def video_feed(request):
    """
    Streaming video feed with real-time detection overlay.
    Uses MJPEG streaming for browser compatibility.
    """
    initialize_detection_system()

    def generate_frames():
        """Generator function that yields video frames."""
        global global_stream, global_detector

        if global_stream is None or global_detector is None:
            # Return error frame
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                error_frame,
                "Camera not available",
                (150, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            return

        try:
            while True:
                frame = global_stream.read_frame()

                if frame is None:
                    break

                # Perform detection
                result = global_detector.detect_safety_violations(frame)

                # Get restricted zones from database
                restricted_zones = []
                zones = RestrictedZone.objects.filter(is_active=True)
                for zone in zones:
                    restricted_zones.append({
                        'name': zone.name,
                        'coordinates': (zone.x1, zone.y1, zone.x2, zone.y2)
                    })

                # Re-detect with restricted zones
                result = global_detector.detect_safety_violations(frame, restricted_zones)

                # Draw overlay
                stats = {
                    'Workers': len(result['detections']),
                    'Violations': len(result['violations'])
                }
                annotated_frame = draw_overlay_info(result['annotated_frame'], stats)

                # Log violations if any
                if result['violations']:
                    process_violations(result['violations'], result['annotated_frame'])

                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()

                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                # Small delay to prevent excessive CPU usage
                cv2.waitKey(1)

        except GeneratorExit:
            logger.info("Video feed client disconnected")
        except Exception as e:
            logger.error(f"Error in video feed: {e}")

    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def process_violations(violations, frame):
    """
    Process detected violations and log them to the database.

    Args:
        violations: List of violation dictionaries
        frame: Current video frame
    """
    # Rate limiting: Only log if last violation was more than 5 seconds ago
    last_violation_time = cache.get('last_violation_time')
    now = timezone.now()

    if last_violation_time and (now - last_violation_time).total_seconds() < 5:
        return

    for violation in violations[:3]:  # Limit to 3 violations per frame
        try:
            # Create incident record
            incident = SafetyIncident(
                camera_id='CAM-01',
                hazard_type=violation['type'],
                confidence_score=violation['confidence'],
                detection_details={
                    'box': violation['box'],
                    'message': violation['message']
                }
            )

            # Save snapshot
            try:
                from django.core.files.base import ContentFile
                from io import BytesIO

                # Save frame as image
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    image_file = ContentFile(buffer.tobytes())
                    filename = f"violation_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                    incident.image_path.save(filename, image_file, save=False)
            except Exception as e:
                logger.error(f"Error saving snapshot: {e}")

            incident.save()
            logger.info(f"Violation logged: {violation['type']}")

        except Exception as e:
            logger.error(f"Error logging violation: {e}")

    # Update cache
    cache.set('last_violation_time', now, timeout=10)


def incidents_api(request):
    """
    API endpoint to fetch incidents data for dashboard.
    Returns JSON with recent incidents and statistics.
    """
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

    # Get recent incidents
    incidents = SafetyIncident.objects.filter(
        timestamp__gte=today_start
    ).order_by('-timestamp')[:20]

    incidents_data = []
    for incident in incidents:
        incidents_data.append({
            'id': incident.incident_id,
            'type': incident.hazard_type,
            'timestamp': incident.timestamp.strftime('%H:%M:%S'),
            'confidence': f"{incident.confidence_percentage}%",
            'resolved': incident.is_resolved,
            'image': incident.image_path.url if incident.image_path else None
        })

    # Get statistics
    stats = {
        'total': SafetyIncident.objects.count(),
        'today': incidents.count(),
        'unresolved': SafetyIncident.objects.filter(is_resolved=False).count(),
        'by_type': {}
    }

    # Group by hazard type
    for incident in incidents:
        hazard_type = incident.hazard_type
        if hazard_type not in stats['by_type']:
            stats['by_type'][hazard_type] = 0
        stats['by_type'][hazard_type] += 1

    return JsonResponse({
        'incidents': incidents_data,
        'stats': stats
    })


def resolve_incident(request, incident_id):
    """
    Mark an incident as resolved.
    """
    if request.method == 'POST':
        try:
            incident = SafetyIncident.objects.get(incident_id=incident_id)
            incident.is_resolved = True
            incident.save()
            return JsonResponse({'success': True})
        except SafetyIncident.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Incident not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def statistics_api(request):
    """
    API endpoint for detailed statistics.
    """
    # Get last 7 days data
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_incidents = SafetyIncident.objects.filter(
        timestamp__gte=seven_days_ago
    )

    # Daily breakdown
    daily_stats = {}
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        count = SafetyIncident.objects.filter(
            timestamp__date=date
        ).count()
        daily_stats[date_str] = count

    # Violation types breakdown
    violation_types = {}
    for incident in recent_incidents:
        vtype = incident.hazard_type
        violation_types[vtype] = violation_types.get(vtype, 0) + 1

    return JsonResponse({
        'daily_stats': daily_stats,
        'violation_types': violation_types,
        'total_week': recent_incidents.count()
    })


def reports(request):
    """
    Reports page with detailed incident history and analytics.
    """
    # Get all incidents with pagination
    incidents_list = SafetyIncident.objects.all().order_by('-timestamp')

    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        incidents_list = incidents_list.filter(timestamp__gte=start_date)
    if end_date:
        incidents_list = incidents_list.filter(timestamp__lte=end_date)

    # Filter by hazard type
    hazard_type = request.GET.get('hazard_type')
    if hazard_type:
        incidents_list = incidents_list.filter(hazard_type=hazard_type)

    # Calculate statistics
    total_incidents = incidents_list.count()
    resolved_count = incidents_list.filter(is_resolved=True).count()
    unresolved_count = incidents_list.filter(is_resolved=False).count()

    context = {
        'page_title': 'Safety Reports',
        'incidents': incidents_list[:100],  # Limit to 100 for display
        'hazard_types': SafetyIncident.HAZARD_TYPES,
        'total_incidents': total_incidents,
        'resolved_count': resolved_count,
        'unresolved_count': unresolved_count,
    }

    return render(request, 'monitoring/reports.html', context)


def settings_page(request):
    """
    Settings page for camera configuration and restricted zones.
    """
    cameras = CameraConfig.objects.all()
    zones = RestrictedZone.objects.filter(is_active=True)

    context = {
        'page_title': 'System Settings',
        'cameras': cameras,
        'zones': zones,
    }

    return render(request, 'monitoring/settings.html', context)


@csrf_exempt
def add_restricted_zone(request):
    """Add a new restricted zone."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            zone = RestrictedZone.objects.create(
                name=data.get('name', 'New Zone'),
                description=data.get('description', ''),
                x1=int(data.get('x1', 0)),
                y1=int(data.get('y1', 0)),
                x2=int(data.get('x2', 100)),
                y2=int(data.get('y2', 100)),
            )
            return JsonResponse({'success': True, 'zone_id': zone.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def system_status(request):
    """
    API endpoint to get system status.
    """
    initialize_detection_system()

    status = {
        'system_online': True,
        'camera_active': global_stream is not None and global_stream.is_opened if global_stream else False,
        'detector_loaded': global_detector is not None and global_detector.model_loaded if global_detector else False,
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    return JsonResponse(status)


@csrf_exempt
def clear_all_incidents(request):
    """
    API endpoint to clear all safety incidents.
    """
    if request.method == 'POST':
        try:
            # Delete all incidents
            count = SafetyIncident.objects.all().count()
            SafetyIncident.objects.all().delete()

            return JsonResponse({
                'success': True,
                'message': f'Cleared {count} incident(s)',
                'count': count
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

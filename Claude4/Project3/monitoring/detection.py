"""
AI Detection Module for Worker Safety System
Handles object detection using OpenCV and pre-trained models.
"""

import cv2
import numpy as np
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SafetyDetector:
    """
    Main class for AI-based safety gear detection.
    Uses OpenCV DNN module with pre-trained models.
    """

    # COCO class names (90 classes)
    COCO_CLASSES = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
        'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
        'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
        'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
        'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
        'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
        'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]

    def __init__(self, confidence_threshold=0.5):
        """
        Initialize the detector with configuration.

        Args:
            confidence_threshold: Minimum confidence for detections (default: 0.5)
        """
        self.confidence_threshold = confidence_threshold
        self.net = None
        self.output_layers = None
        self.model_loaded = False

        # Try to load pre-trained model
        self._load_model()

    def _load_model(self):
        """
        Load the pre-trained object detection model.
        Attempts to load MobileNet-SSD model for faster inference.
        """
        try:
            # Model files will be downloaded if not present
            model_dir = Path(__file__).parent.parent / 'models'
            model_dir.mkdir(exist_ok=True)

            # MobileNet SSD v2 model paths
            proto_path = model_dir / 'MobileNetSSD_deploy.prototxt'
            model_path = model_dir / 'MobileNetSSD_deploy.caffemodel'

            if proto_path.exists() and model_path.exists():
                logger.info("Loading MobileNet SSD model...")
                self.net = cv2.dnn.readNetFromCaffe(str(proto_path), str(model_path))
                self.model_loaded = True
                logger.info("Model loaded successfully!")
            else:
                logger.warning(
                    "Model files not found. Using fallback detection method. "
                    "Download MobileNet SSD model for better results."
                )
                self.model_loaded = False

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model_loaded = False

    def detect_objects(self, frame):
        """
        Perform object detection on a frame.

        Args:
            frame: Input image frame (numpy array)

        Returns:
            List of detections with format:
            [{'class': 'person', 'confidence': 0.85, 'box': (x, y, w, h)}, ...]
        """
        detections = []

        if self.model_loaded and self.net is not None:
            try:
                # Prepare the frame for detection
                (h, w) = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(
                    frame,
                    0.007843,
                    (300, 300),
                    (127.5, 127.5, 127.5),
                    swapRB=False,
                    crop=False
                )

                # Pass the blob through the network
                self.net.setInput(blob)
                predictions = self.net.forward()

                # Loop over the predictions
                for i in range(predictions.shape[2]):
                    confidence = predictions[0, 0, i, 2]

                    # Filter out weak predictions
                    if confidence > self.confidence_threshold:
                        class_id = int(predictions[0, 0, i, 1])

                        # Get bounding box coordinates
                        box = predictions[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # Add to detections list
                        detections.append({
                            'class': self.COCO_CLASSES[class_id] if class_id < len(self.COCO_CLASSES) else 'unknown',
                            'confidence': float(confidence),
                            'box': (startX, startY, endX - startX, endY - startY)
                        })

            except Exception as e:
                logger.error(f"Error during detection: {e}")
        else:
            # Fallback: Simple motion/person detection using Haar Cascade
            detections = self._fallback_detection(frame)

        return detections

    def _fallback_detection(self, frame):
        """
        Fallback detection using Haar Cascades.
        Less accurate but works without external models.
        """
        detections = []

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Use Haar Cascade for full body detection
            haar_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            if Path(haar_path).exists():
                cascade = cv2.CascadeClassifier(haar_path)
                bodies = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                for (x, y, w, h) in bodies:
                    detections.append({
                        'class': 'person',
                        'confidence': 0.7,  # Default confidence for Haar
                        'box': (int(x), int(y), int(w), int(h))
                    })
        except Exception as e:
            logger.error(f"Error in fallback detection: {e}")

        return detections

    def detect_safety_violations(self, frame, restricted_zones=None):
        """
        Detect safety violations in the frame.

        Args:
            frame: Input image frame
            restricted_zones: List of restricted zone dictionaries

        Returns:
            Dictionary with:
            - 'detections': All detected objects
            - 'violations': List of safety violations found
            - 'annotated_frame': Frame with bounding boxes drawn
        """
        detections = self.detect_objects(frame)
        violations = []

        # Create annotated frame
        annotated_frame = frame.copy()

        # Draw restricted zones
        if restricted_zones:
            for zone in restricted_zones:
                coords = zone.get('coordinates', (0, 0, 0, 0))
                x1, y1, x2, y2 = coords
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    annotated_frame,
                    "RESTRICTED",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2
                )

        # Process each detection
        for detection in detections:
            class_name = detection['class']
            confidence = detection['confidence']
            x, y, w, h = detection['box']

            # For demonstration: We'll assume all detected persons
            # need safety gear (helmet + vest)
            # In production, you'd train a custom model to detect
            # helmets and vests specifically

            if class_name == 'person':
                # Check if person is in restricted zone
                center_x = x + w // 2
                center_y = y + h // 2

                in_restricted_zone = False
                if restricted_zones:
                    for zone in restricted_zones:
                        coords = zone.get('coordinates', (0, 0, 0, 0))
                        x1, y1, x2, y2 = coords
                        if x1 <= center_x <= x2 and y1 <= center_y <= y2:
                            in_restricted_zone = True
                            violations.append({
                                'type': 'RESTRICTED_ZONE',
                                'confidence': confidence,
                                'message': 'Person in restricted zone',
                                'box': (x, y, w, h)
                            })
                            break

                # For demonstration: Flag all persons as potential violations
                # In production, check for actual PPE detection
                violations.append({
                    'type': 'NO_PPE',
                    'confidence': confidence * 0.8,  # Slightly lower confidence for PPE assumption
                    'message': 'Person without verified PPE',
                    'box': (x, y, w, h)
                })

                # Draw bounding box for person
                color = (0, 255, 0) if not in_restricted_zone else (0, 0, 255)
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    annotated_frame,
                    f"Person {confidence:.2f}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

        return {
            'detections': detections,
            'violations': violations,
            'annotated_frame': annotated_frame
        }

    def get_detection_summary(self, detections):
        """
        Get a summary of detections (counts by class).

        Args:
            detections: List of detection dictionaries

        Returns:
            Dictionary with class counts
        """
        summary = {'person': 0}

        for detection in detections:
            class_name = detection['class']
            if class_name in summary:
                summary[class_name] += 1
            else:
                summary[class_name] = 1

        return summary


class VideoStream:
    """
    Video stream handler for webcams and video files.
    """

    def __init__(self, source=0):
        """
        Initialize video stream.

        Args:
            source: Camera index (0, 1, ...) or video file path
        """
        self.source = source
        self.cap = None
        self.is_opened = False

    def start(self):
        """Open the video stream."""
        try:
            self.cap = cv2.VideoCapture(self.source)
            self.is_opened = self.cap.isOpened()

            if self.is_opened:
                # Set reasonable resolution
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                logger.info(f"Video stream started: {self.source}")
            else:
                logger.error(f"Failed to open video stream: {self.source}")

        except Exception as e:
            logger.error(f"Error starting video stream: {e}")

        return self.is_opened

    def read_frame(self):
        """
        Read a single frame from the stream.

        Returns:
            frame (numpy array) or None if failed
        """
        if self.cap is None or not self.is_opened:
            return None

        ret, frame = self.cap.read()

        if ret:
            return frame
        else:
            logger.warning("Failed to read frame from video stream")
            return None

    def release(self):
        """Release the video stream."""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            logger.info("Video stream released")


def draw_overlay_info(frame, stats=None):
    """
    Draw information overlay on the frame.

    Args:
        frame: Input frame
        stats: Dictionary with statistics to display

    Returns:
        Frame with overlay drawn
    """
    overlay = frame.copy()

    # Semi-transparent background for info panel
    panel_height = 100
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], panel_height), (0, 0, 0), -1)

    # Add transparency
    alpha = 0.6
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Draw timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        frame,
        timestamp,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Draw statistics
    if stats:
        y_offset = 60
        for key, value in stats.items():
            text = f"{key}: {value}"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y_offset += 25

    return frame

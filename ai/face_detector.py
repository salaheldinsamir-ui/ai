"""
Face Detection Module
Detects and validates faces in camera frames
"""
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MIN_BRIGHTNESS, MIN_CONTRAST, MIN_SHARPNESS


class FaceDetector:
    """Detects faces from camera frames using OpenCV"""
    
    def __init__(self, backend="opencv"):
        """
        Initialize face detector
        
        Args:
            backend: Detection backend ("opencv", "dlib", "mtcnn", etc.)
        """
        self.backend = backend
        
        if backend == "opencv":
            # Load Haar Cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            
    def detect_faces(self, frame):
        """
        Detect faces in a frame
        
        Args:
            frame: Input image frame (BGR)
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
        
    def get_single_face(self, frame):
        """
        Detect and return single face from frame
        Ensures only one face is present for security
        
        Args:
            frame: Input image frame (BGR)
            
        Returns:
            Tuple: (cropped_face, bbox) or (None, None) if validation fails
        """
        faces = self.detect_faces(frame)
        
        # Ensure exactly one face is detected
        if len(faces) != 1:
            return None, None
            
        x, y, w, h = faces[0]
        
        # Add margin around face
        margin = 20
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)
        
        # Crop face region
        face_roi = frame[y1:y2, x1:x2]
        
        # Validate face size and quality
        if face_roi.shape[0] < 80 or face_roi.shape[1] < 80:
            return None, None
            
        return face_roi, (x, y, w, h)
        
    def draw_faces(self, frame, faces):
        """
        Draw bounding boxes around detected faces
        
        Args:
            frame: Input image frame (BGR)
            faces: List of face bounding boxes
            
        Returns:
            Frame with drawn bounding boxes
        """
        output = frame.copy()
        
        for (x, y, w, h) in faces:
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(output, "Face", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                       
        return output
        
    def validate_face_quality(self, face_roi):
        """
        Validate face image quality (relaxed thresholds for poor lighting)
        
        Args:
            face_roi: Cropped face region
            
        Returns:
            True if quality is sufficient, False otherwise
        """
        # Check if image is too dark (using config threshold)
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness < MIN_BRIGHTNESS:  # Too dark
            return False
            
        # Check contrast (using config threshold)
        contrast = gray.std()
        if contrast < MIN_CONTRAST:  # Too low contrast
            return False
            
        # Check for blur (using config threshold)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < MIN_SHARPNESS:  # Too blurry
            return False
            
        return True

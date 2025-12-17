"""
ArUco Marker Detection Module
Detects and decodes ArUco markers for secondary authentication
"""
import cv2
import numpy as np


class ArucoDetector:
    """Detects ArUco markers from camera frames"""
    
    def __init__(self, dictionary="DICT_4X4_50"):
        """
        Initialize ArUco detector
        
        Args:
            dictionary: ArUco dictionary type
        """
        # Get ArUco dictionary
        aruco_dict_mapping = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
        }
        
        dict_type = aruco_dict_mapping.get(dictionary, cv2.aruco.DICT_4X4_50)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
    def detect_markers(self, frame):
        """
        Detect ArUco markers in a frame
        
        Args:
            frame: Input image frame (BGR)
            
        Returns:
            List of detected marker IDs
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, rejected = self.detector.detectMarkers(gray)
        
        # Extract marker IDs
        marker_ids = []
        if ids is not None:
            marker_ids = ids.flatten().tolist()
            
        return marker_ids, corners
        
    def get_single_marker(self, frame):
        """
        Detect and return single ArUco marker
        Ensures only one marker is present for security
        
        Args:
            frame: Input image frame (BGR)
            
        Returns:
            ArUco ID or None if validation fails
        """
        marker_ids, corners = self.detect_markers(frame)
        
        # Ensure exactly one marker is detected
        if len(marker_ids) != 1:
            return None
            
        return marker_ids[0]
        
    def draw_markers(self, frame, corners, ids):
        """
        Draw detected markers on frame
        
        Args:
            frame: Input image frame (BGR)
            corners: Marker corners
            ids: Marker IDs
            
        Returns:
            Frame with drawn markers
        """
        output = frame.copy()
        
        if ids is not None and len(ids) > 0:
            # Convert ids to numpy array if it's a list
            import numpy as np
            if isinstance(ids, list):
                ids = np.array(ids).reshape(-1, 1)
            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(output, corners, ids)
            
        return output
        
    def validate_marker_quality(self, corners):
        """
        Validate ArUco marker detection quality
        
        Args:
            corners: Detected marker corners
            
        Returns:
            True if quality is sufficient, False otherwise
        """
        if corners is None or len(corners) == 0:
            return False
            
        # Check marker size (should be reasonably large)
        corner_points = corners[0][0]
        width = np.linalg.norm(corner_points[0] - corner_points[1])
        height = np.linalg.norm(corner_points[0] - corner_points[3])
        
        # Marker should be at least 50x50 pixels
        if width < 50 or height < 50:
            return False
            
        return True
        
    def generate_marker(self, marker_id, size=200):
        """
        Generate an ArUco marker image for printing
        
        Args:
            marker_id: Marker ID to generate
            size: Size of marker image in pixels
            
        Returns:
            Marker image
        """
        marker_img = cv2.aruco.generateImageMarker(self.aruco_dict, marker_id, size)
        return marker_img

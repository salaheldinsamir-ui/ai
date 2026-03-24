"""
Attendance Decision Engine - FIXED VERSION
Validates all conditions before marking attendance with ArUco retry logic
"""
import cv2
import time
from datetime import datetime


class AttendanceEngine:
    """
    Core attendance logic - Step-by-step process:
    1. Presence detection (ultrasonic sensors)
    2. Single face detection
    3. Face recognition above threshold
    4. Ask user to show ArUco marker
    5. Wait for ArUco detection
    6. Verify ArUco ID matches recognized student
    7. Display student name and mark attendance
    """
    
    def __init__(self, db_manager, face_detector, face_recognizer, aruco_detector,
                 ultrasonic_sensor1, ultrasonic_sensor2, lcd, buzzer, threshold=0.6):
        """
        Initialize attendance engine
        
        Args:
            db_manager: Database manager instance
            face_detector: Face detector instance
            face_recognizer: Face recognizer instance
            aruco_detector: ArUco detector instance
            ultrasonic_sensor1: First ultrasonic sensor
            ultrasonic_sensor2: Second ultrasonic sensor
            lcd: LCD display instance
            buzzer: Buzzer instance
            threshold: Face recognition threshold
        """
        self.db = db_manager
        self.face_detector = face_detector
        self.face_recognizer = face_recognizer
        self.aruco_detector = aruco_detector
        self.ultrasonic1 = ultrasonic_sensor1
        self.ultrasonic2 = ultrasonic_sensor2
        self.lcd = lcd
        self.buzzer = buzzer
        self.threshold = threshold
        
        # State management for step-by-step process
        self.current_state = "IDLE"  # Start in IDLE, activate when presence detected
        self.recognized_student = None  # Store recognized student info
        self.detected_aruco_id = None  # Store detected ArUco ID
        self.display_message_frame = None  # Store frame for display
        self.displaying_message = False  # Flag to skip presence check during message display
        self.message_display_time = 5.0  # Time to show success/error messages
        self.state_start_time = time.time()
        self.face_wait_time = 5.0  # Seconds to wait before detecting face
        self.aruco_wait_time = 5.0  # Seconds to wait before detecting ArUco
        self.detection_start_time = None  # When actual detection started
        
        # Presence tracking for idle timeout
        self.last_presence_time = None  # Last time presence was detected
        self.idle_timeout = 10.0  # Seconds of no presence before going idle
        self.presence_distance = 45  # Detection distance in cm
        
        # Face stability tracking
        self.face_stable_start = None  # When stable face detection started
        self.last_face_position = None  # Last detected face position (x, y, w, h)
        self.face_stability_threshold = 2.5  # Seconds face must be stable
        self.position_tolerance = 30  # Pixels tolerance for "stable" position
        
        # NEW: Retry logic for ArUco
        self.aruco_retry_count = 0
        self.max_aruco_retries = 3  # Allow 3 attempts before full reset
        
        # Load all students from database
        self.students_db = db_manager.get_all_students()
        print(f"[Engine] Loaded {len(self.students_db)} students from database")
        
    def check_presence(self, min_distance=30, max_distance=100):
        """
        Check if presence is detected by both ultrasonic sensors
        
        Returns:
            True if presence detected within valid range
        """
        # Import config to check if ultrasonic is enabled
        from config import ULTRASONIC_ENABLED
        
        # If ultrasonic sensors are disabled, always return True (presence assumed)
        if not ULTRASONIC_ENABLED:
            return True
        
        # Check both sensors
        presence1 = self.ultrasonic1.check_presence(min_distance, max_distance)
        presence2 = self.ultrasonic2.check_presence(min_distance, max_distance)
        
        # Both sensors must detect presence
        return presence1 and presence2
        
        
    def reset_state(self, full_reset=True):
        """
        Reset to initial state
        
        Args:
            full_reset: If True, reset everything including recognized student
                       If False, only reset to ArUco detection (for retries)
        """
        if full_reset:
            self.current_state = "WAITING_FOR_FACE"  # Go back to waiting for face, not IDLE
            self.recognized_student = None
            self.aruco_retry_count = 0
            self.displaying_message = False
            self.face_stable_start = None
            self.last_face_position = None
        else:
            # Partial reset - go back to ArUco waiting (keep recognized student)
            self.current_state = "WAITING_FOR_ARUCO"
            
        self.state_start_time = time.time()
        self.detection_start_time = None
        
    def process_frame(self, frame):
        """
        Process a single frame with step-by-step workflow with calm 5-second waits
        
        Args:
            frame: Camera frame (BGR)
            
        Returns:
            Tuple: (success, message, processed_frame)
        """
        display_frame = frame.copy()
        current_time = time.time()
        
        # STATE 0: IDLE (System sleeping, waiting for presence)
        if self.current_state == "IDLE":
            cv2.putText(display_frame, "System in Standby Mode", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 2)
            cv2.putText(display_frame, "Approach to activate", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
            
            # Check if presence detected to wake up
            if self.check_presence(min_distance=10, max_distance=self.presence_distance):
                self.current_state = "WAITING_FOR_FACE"
                self.last_presence_time = current_time
                self.state_start_time = current_time
                cv2.putText(display_frame, "System Activated!", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            return False, "idle", display_frame
        
        # STATE 1: WAITING FOR FACE (Continuous monitoring - wait for stable face)
        if self.current_state == "WAITING_FOR_FACE":
            # Try to detect face
            face_roi, face_bbox = self.face_detector.get_single_face(frame)
            
            if face_roi is not None:
                x, y, w, h = face_bbox
                
                # Check if face position is stable
                if self.last_face_position is not None:
                    # Calculate distance from last position
                    last_x, last_y, last_w, last_h = self.last_face_position
                    distance = abs(x - last_x) + abs(y - last_y)
                    
                    if distance < self.position_tolerance:
                        # Face is stable, check how long
                        if self.face_stable_start is None:
                            self.face_stable_start = current_time
                        
                        elapsed = current_time - self.face_stable_start
                        remaining = int(self.face_stability_threshold - elapsed)
                        
                        # Draw face box and stability indicator
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                        
                        if remaining > 0:
                            cv2.putText(display_frame, f"Hold still... {remaining}s", (10, 50),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                            # Draw progress bar
                            progress = int((elapsed / self.face_stability_threshold) * 300)
                            cv2.rectangle(display_frame, (10, 80), (10 + progress, 100), (0, 255, 255), -1)
                            cv2.rectangle(display_frame, (10, 80), (310, 100), (255, 255, 255), 2)
                        else:
                            # Face has been stable for 5 seconds - start recognition
                            self.current_state = "DETECTING_FACE"
                            self.detection_start_time = current_time
                            cv2.putText(display_frame, "Starting recognition...", (10, 50),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                    else:
                        # Face moved - reset timer
                        self.face_stable_start = None
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                        cv2.putText(display_frame, "Hold still...", (10, 50),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                else:
                    # First face detection
                    self.face_stable_start = None
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                    cv2.putText(display_frame, "Hold still...", (10, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                
                # Update last position
                self.last_face_position = (x, y, w, h)
            else:
                # No face detected
                self.face_stable_start = None
                self.last_face_position = None
                cv2.putText(display_frame, "Attendance System Ready", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                cv2.putText(display_frame, "Show your face to begin", (10, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            
            return False, "waiting_for_stable_face", display_frame
        
        # STATE 2: DETECTING FACE (Try to detect for 5 seconds)
        elif self.current_state == "DETECTING_FACE":
            elapsed = current_time - self.detection_start_time
            
            cv2.putText(display_frame, "Detecting your face...", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Try to detect face
            face_roi, face_bbox = self.face_detector.get_single_face(frame)
            
            if face_roi is not None:
                # Draw face bounding box
                x, y, w, h = face_bbox
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Quality check removed - proceed directly to recognition
                # Let cosine similarity determine if face quality is sufficient
                
                # Recognize face
                student_id, name, expected_aruco, similarity = self.face_recognizer.recognize_face(
                    face_roi, self.students_db, self.threshold
                )
                
                if student_id is None:
                    cv2.putText(display_frame, "Face not recognized", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Timeout - retry
                    if elapsed > self.face_wait_time:
                        self.reset_state(full_reset=True)
                    return False, "not_recognized", display_frame
                
                # Face recognized! Move to next state
                cv2.putText(display_frame, f"Welcome {name}!", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                self.recognized_student = {
                    'id': student_id,
                    'name': name,
                    'expected_aruco': expected_aruco,
                    'similarity': similarity
                }
                self.current_state = "WAITING_FOR_ARUCO"
                self.state_start_time = current_time
                self.detection_start_time = None
                self.aruco_retry_count = 0  # Reset retry counter
                
                return False, "face_recognized", display_frame
            else:
                # No face detected
                faces = self.face_detector.detect_faces(frame)
                if len(faces) > 1:
                    cv2.putText(display_frame, "Multiple faces! Only one person", (10, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(display_frame, "No face detected", (10, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Timeout - retry
                if elapsed > self.face_wait_time:
                    self.reset_state(full_reset=True)
                    return False, "face_timeout", display_frame
                
                return False, "no_face", display_frame
        
        # STATE 3: WAITING FOR ARUCO (Initial prompt - 5 seconds)
        elif self.current_state == "WAITING_FOR_ARUCO":
            elapsed = current_time - self.state_start_time
            
            # Show instruction for 5 seconds
            cv2.putText(display_frame, f"Show your ArUco marker", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(display_frame, f"Student: {self.recognized_student['name']}", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show retry count if retrying
            if self.aruco_retry_count > 0:
                cv2.putText(display_frame, f"Attempt {self.aruco_retry_count + 1}/{self.max_aruco_retries + 1}", 
                           (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            
            remaining = int(self.aruco_wait_time - elapsed)
            if remaining > 0:
                cv2.putText(display_frame, f"Get ready... {remaining}s", (10, 200),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                return False, "waiting_aruco_instruction", display_frame
            
            # After 5 seconds, start detecting
            self.current_state = "DETECTING_ARUCO"
            self.detection_start_time = current_time
            return False, "start_detecting_aruco", display_frame
        
        # STATE 4: DETECTING ARUCO (Try to detect for 5 seconds)
        elif self.current_state == "DETECTING_ARUCO":
            elapsed = current_time - self.detection_start_time
            
            cv2.putText(display_frame, "Detecting ArUco marker...", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Expected ID: {self.recognized_student['expected_aruco']}", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Detect ArUco markers
            marker_ids, corners = self.aruco_detector.detect_markers(frame)
            
            # Debug: Draw all detected markers
            if len(marker_ids) > 0:
                display_frame = self.aruco_detector.draw_markers(display_frame, corners, marker_ids)
                cv2.putText(display_frame, f"Detected IDs: {marker_ids}", (10, 200),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Check if exactly one marker detected
            detected_aruco = None
            if len(marker_ids) == 1:
                detected_aruco = marker_ids[0]
            
            if detected_aruco is not None:
                # Verify ArUco matches student
                if detected_aruco != self.recognized_student['expected_aruco']:
                    cv2.putText(display_frame, f"Wrong ArUco! Expected: {self.recognized_student['expected_aruco']}, Got: {detected_aruco}",
                               (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Timeout - retry ArUco only
                    if elapsed > self.aruco_wait_time:
                        self.aruco_retry_count += 1
                        if self.aruco_retry_count >= self.max_aruco_retries:
                            # Too many retries - full reset
                            self.reset_state(full_reset=True)
                        else:
                            # Retry ArUco detection
                            self.reset_state(full_reset=False)
                    return False, "mismatch", display_frame
                
                # ArUco matches! Check if already marked today
                if self.db.check_attendance_today(self.recognized_student['id']):
                    cv2.putText(display_frame, "Already marked today!", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    time.sleep(2)
                    self.reset_state(full_reset=True)
                    return False, "already_marked", display_frame
                
                # Mark attendance
                success = self.db.mark_attendance(self.recognized_student['id'])
                
                if success:
                    cv2.putText(display_frame, f"Attendance Checked", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    cv2.putText(display_frame, f"{self.recognized_student['name']}", (10, 220),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    
                    student_info = (self.recognized_student['name'], self.recognized_student['expected_aruco'])
                    self.display_message_frame = display_frame.copy()
                    self.displaying_message = True
                    self.current_state = "SHOW_SUCCESS"
                    self.state_start_time = current_time
                    return True, student_info, display_frame
                else:
                    cv2.putText(display_frame, "Database Error!", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    self.display_message_frame = display_frame.copy()
                    self.displaying_message = True
                    self.current_state = "SHOW_ERROR"
                    self.state_start_time = current_time
                    return False, "database_error", display_frame
            else:
                # No ArUco detected or multiple markers
                if len(marker_ids) > 1:
                    cv2.putText(display_frame, "Multiple markers! Show only one", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(display_frame, "No ArUco detected", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Timeout - retry ArUco detection
                if elapsed > self.aruco_wait_time:
                    self.aruco_retry_count += 1
                    
                    if self.aruco_retry_count >= self.max_aruco_retries:
                        # Too many retries - show error and full reset
                        cv2.putText(display_frame, "ERROR: Cannot read ArUco!", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                        cv2.putText(display_frame, "Starting over...", (10, 210),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        self.display_message_frame = display_frame.copy()
                        self.displaying_message = True
                        self.current_state = "SHOW_ERROR"
                        self.state_start_time = current_time
                        return False, "aruco_timeout", display_frame
                    else:
                        # Retry ArUco detection (keep recognized student)
                        self.reset_state(full_reset=False)
                        return False, "aruco_retry", display_frame
                
                return False, "no_aruco", display_frame
        
        # STATE 5: SHOW SUCCESS (Display confirmation for 5 seconds)
        elif self.current_state == "SHOW_SUCCESS":
            elapsed = current_time - self.state_start_time
            
            # Keep showing the success frame
            if elapsed < self.message_display_time:
                return False, "showing_success", self.display_message_frame
            else:
                # Done showing, full reset
                self.displaying_message = False
                self.reset_state(full_reset=True)
                return False, "success_displayed", frame
        
        # STATE 6: SHOW ERROR (Display error for 3 seconds)
        elif self.current_state == "SHOW_ERROR":
            elapsed = current_time - self.state_start_time
            
            # Keep showing the error frame  
            if elapsed < 3.0:
                return False, "showing_error", self.display_message_frame
            else:
                # Done showing, full reset (always reset after error display)
                self.displaying_message = False
                self.reset_state(full_reset=True)
                return False, "error_displayed", frame
        
        return False, "unknown_state", display_frame
            
    def run_attendance_check(self, frame):
        """
        Main attendance check pipeline
        
        Args:
            frame: Camera frame
            
        Returns:
            Tuple: (success, message, processed_frame)
        """
        current_time = time.time()
        
        # If displaying messages, just continue showing them (don't process new frames)
        if self.displaying_message:
            if self.current_state == "SHOW_SUCCESS":
                elapsed = time.time() - self.state_start_time
                if elapsed < self.message_display_time:
                    return False, "showing_success", self.display_message_frame
                else:
                    self.displaying_message = False
                    self.reset_state(full_reset=True)
                    return False, "success_displayed", frame
            elif self.current_state == "SHOW_ERROR":
                elapsed = time.time() - self.state_start_time
                if elapsed < 3.0:
                    return False, "showing_error", self.display_message_frame
                else:
                    self.displaying_message = False
                    self.reset_state(full_reset=True)
                    return False, "error_displayed", frame
        
        # Check presence (except when in IDLE)
        if self.current_state != "IDLE":
            presence = self.check_presence(min_distance=10, max_distance=self.presence_distance)
            
            if presence:
                # Update last presence time
                self.last_presence_time = current_time
            else:
                # No presence - check if timeout reached
                if self.last_presence_time is not None:
                    idle_elapsed = current_time - self.last_presence_time
                    if idle_elapsed > self.idle_timeout:
                        # No presence for 10 seconds - go to IDLE
                        print(f"\n[System] No presence detected for {self.idle_timeout}s - Going to standby mode")
                        self.current_state = "IDLE"
                        self.reset_state(full_reset=True)
                        self.current_state = "IDLE"  # Override reset to stay in IDLE
                        self.last_presence_time = None
                        return False, "entering_idle", frame
            
        # Process frame for attendance
        return self.process_frame(frame)
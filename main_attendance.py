"""
Main Attendance System Program
Auto-starts on boot and continuously checks attendance
Robust version with multi-frame capture for Raspberry Pi
"""
import cv2
import sys
import time
import numpy as np
from datetime import datetime

# Import configuration
from config import *

# Import modules
from database.db_manager import DatabaseManager
from ai.face_detector import FaceDetector
from ai.face_recognition import FaceRecognizer
from ai.aruco_detector import ArucoDetector
from hardware.camera import Camera
from hardware.ultrasonic import UltrasonicSensor
from hardware.lcd import LCDDisplay
from hardware.buzzer import Buzzer


class AttendanceSystem:
    """Main attendance system application with robust multi-frame capture"""
    
    def __init__(self):
        """Initialize all system components"""
        print("="*50)
        print("AI-POWERED ATTENDANCE SYSTEM")
        print("="*50)
        print(f"Hardware Mode: {HARDWARE_MODE}")
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Initialize hardware
        print("\n[Init] Initializing hardware components...")
        self.camera = Camera(
            mode=HARDWARE_MODE,
            camera_index=CAMERA_INDEX,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT
        )
        
        # Camera warmup - critical for Raspberry Pi
        print("[Init] Warming up camera...")
        self.lcd = LCDDisplay(
            mode=HARDWARE_MODE,
            i2c_address=LCD_I2C_ADDRESS,
            rows=LCD_ROWS,
            cols=LCD_COLS
        )
        self.lcd.display_message("Starting...", "Camera warmup")
        
        for i in range(15):
            frame = self.camera.read_frame()
            if frame is not None:
                print(f"[Init] Camera warmup frame {i+1}/15")
            time.sleep(0.1)
        print("[Init] Camera warmed up!")
        
        self.ultrasonic1 = UltrasonicSensor(
            mode=HARDWARE_MODE,
            trigger_pin=ULTRASONIC_SENSOR_1_TRIGGER,
            echo_pin=ULTRASONIC_SENSOR_1_ECHO
        )
        
        self.ultrasonic2 = UltrasonicSensor(
            mode=HARDWARE_MODE,
            trigger_pin=ULTRASONIC_SENSOR_2_TRIGGER,
            echo_pin=ULTRASONIC_SENSOR_2_ECHO
        )
        
        self.buzzer = Buzzer(
            mode=HARDWARE_MODE,
            pin=BUZZER_PIN
        )
        
        # Initialize AI modules
        print("\n[Init] Initializing AI modules...")
        self.lcd.display_message("Loading AI...", "Please wait")
        self.face_detector = FaceDetector(backend=FACE_DETECTION_BACKEND)
        self.face_recognizer = FaceRecognizer(model_name=FACE_MODEL, backend=FACE_DETECTION_BACKEND)
        self.aruco_detector = ArucoDetector(dictionary=ARUCO_DICT)
        
        # Initialize database
        print("\n[Init] Connecting to database...")
        self.db = DatabaseManager(DATABASE_PATH)
        student_count = self.db.get_student_count()
        print(f"[Init] Database loaded: {student_count} students enrolled")
        
        # Load all students for recognition
        self.students_db = self.db.get_all_students()
        print(f"[Init] Loaded {len(self.students_db)} students for recognition")
        
        if student_count == 0:
            print("\n[Warning] No students enrolled! Please run enroll_students.py first.")
            self.lcd.display_message("No Students", "Enrolled!")
            self.buzzer.error_tone()
            time.sleep(3)
        
        print("\n[Init] System initialization complete!")
        self.lcd.display_message("System Ready", "Show your face")
        self.buzzer.success_tone()
        
    def capture_multi_frame(self, num_frames=15, max_retries=60):
        """
        Capture multiple frames and return the best quality one
        Similar to enrollment approach for robustness
        
        Args:
            num_frames: Number of frames to capture
            max_retries: Maximum retry attempts
            
        Returns:
            Best quality frame or None
        """
        frames = []
        retry_count = 0
        
        while len(frames) < num_frames and retry_count < max_retries:
            frame = self.camera.read_frame()
            if frame is not None:
                frames.append(frame)
            else:
                retry_count += 1
                time.sleep(0.05)
        
        if len(frames) == 0:
            return None
        
        # Select best quality frame based on sharpness
        best_frame = None
        best_score = 0
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            if score > best_score:
                best_score = score
                best_frame = frame
        
        return best_frame
    
    def check_presence(self, max_distance=45):
        """
        Check if someone is present within range using ultrasonic sensors
        
        Args:
            max_distance: Maximum detection distance in cm (default 45cm)
            
        Returns:
            True if presence detected, False otherwise
        """
        if not ULTRASONIC_ENABLED:
            return True
        
        # Check both sensors - either one detecting is enough
        presence1 = self.ultrasonic1.check_presence(10, max_distance)
        presence2 = self.ultrasonic2.check_presence(10, max_distance)
        return presence1 or presence2
    
    def run(self):
        """Main attendance checking loop - with ultrasonic presence detection"""
        print("\n" + "="*50)
        print("ATTENDANCE SYSTEM ACTIVE")
        print("Press Ctrl+C to quit")
        print("="*50 + "\n")
        
        # State machine
        STATE_STANDBY = -1      # System sleeping, waiting for presence
        STATE_WAITING = 0       # Active, waiting for face
        STATE_DETECTING_FACE = 1
        STATE_WAITING_ARUCO = 2
        STATE_DETECTING_ARUCO = 3
        STATE_SUCCESS = 4
        STATE_ERROR = 5
        
        # Start in standby if ultrasonic is enabled, otherwise start active
        if ULTRASONIC_ENABLED:
            current_state = STATE_STANDBY
            self.lcd.display_message("System", "Standby Mode")
            print("[System] Starting in STANDBY mode - waiting for presence")
        else:
            current_state = STATE_WAITING
            self.lcd.display_message("Ready", "Show your face")
            print("[System] Ultrasonic disabled - system always active")
        
        recognized_student = None
        state_start_time = time.time()
        last_presence_time = time.time()  # Track when presence was last detected
        no_presence_timeout = 10.0  # Seconds of no presence before going to standby
        
        try:
            while True:
                current_time = time.time()
                
                # ===== STATE: STANDBY (waiting for presence) =====
                if current_state == STATE_STANDBY:
                    # Check for presence
                    if self.check_presence(max_distance=45):
                        print("\n[System] Presence detected! Waking up...")
                        self.lcd.display_message("Welcome!", "Initializing...")
                        self.buzzer.beep(0.1)
                        time.sleep(0.5)
                        
                        current_state = STATE_WAITING
                        last_presence_time = current_time
                        state_start_time = current_time
                        self.lcd.display_message("Ready", "Show your face")
                    else:
                        # Still in standby - minimal processing
                        time.sleep(0.5)  # Check presence every 0.5 seconds
                    continue
                
                # For all active states, check presence timeout
                if ULTRASONIC_ENABLED:
                    if self.check_presence(max_distance=45):
                        last_presence_time = current_time
                    else:
                        # No presence - check timeout
                        no_presence_duration = current_time - last_presence_time
                        if no_presence_duration >= no_presence_timeout:
                            print(f"\n[System] No presence for {no_presence_timeout}s - going to STANDBY")
                            self.lcd.display_message("System", "Standby Mode")
                            current_state = STATE_STANDBY
                            recognized_student = None
                            continue
                
                # ===== STATE: WAITING FOR FACE =====
                if current_state == STATE_WAITING:
                    self.lcd.display_message("Attendance", "Show your face")
                    
                    # Capture best frame
                    frame = self.capture_multi_frame(num_frames=10)
                    if frame is None:
                        print("[Error] Failed to capture frame")
                        time.sleep(0.5)
                        continue
                    
                    # Try to detect face
                    face_roi, face_bbox = self.face_detector.get_single_face(frame)
                    
                    if face_roi is not None:
                        x, y, w, h = face_bbox
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, "Face detected!", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Move to face detection state
                        current_state = STATE_DETECTING_FACE
                        state_start_time = current_time
                        print("\n[Attendance] Face detected, starting recognition...")
                        self.lcd.display_message("Face Found", "Recognizing...")
                        self.buzzer.beep(0.1)
                    else:
                        cv2.putText(frame, "Show your face to camera", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    if HARDWARE_MODE == "PC":
                        cv2.imshow("Attendance System", frame)
                        key = cv2.waitKey(100) & 0xFF
                        if key == ord('q'):
                            break
                        elif key == ord('s'):
                            self.show_statistics()
                    else:
                        time.sleep(0.1)
                
                # ===== STATE: DETECTING & RECOGNIZING FACE =====
                elif current_state == STATE_DETECTING_FACE:
                    self.lcd.display_message("Recognizing", "Please wait...")
                    
                    # Capture best quality frame for recognition
                    frame = self.capture_multi_frame(num_frames=15)
                    if frame is None:
                        current_state = STATE_WAITING
                        continue
                    
                    # Get face ROI
                    face_roi, face_bbox = self.face_detector.get_single_face(frame)
                    
                    if face_roi is None:
                        # Face lost, go back to waiting
                        elapsed = current_time - state_start_time
                        if elapsed > 5.0:
                            print("[Attendance] Face lost, going back to waiting")
                            self.lcd.display_message("Face Lost", "Try again")
                            self.buzzer.error_tone()
                            current_state = STATE_WAITING
                            time.sleep(1)
                        continue
                    
                    # Draw face box
                    x, y, w, h = face_bbox
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Recognize face
                    print("[Attendance] Recognizing face...")
                    student_id, name, aruco_id, similarity = self.face_recognizer.recognize_face(
                        face_roi, self.students_db, FACE_RECOGNITION_THRESHOLD
                    )
                    
                    if student_id is not None:
                        # Face recognized!
                        recognized_student = {
                            'id': student_id,
                            'name': name,
                            'aruco_id': aruco_id,
                            'similarity': similarity
                        }
                        print(f"[Attendance] Recognized: {name} (similarity: {similarity:.2f})")
                        cv2.putText(frame, f"Hello, {name}!", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        # Show Hello message first
                        self.lcd.display_message(f"Hello", f"{name[:16]}")
                        self.buzzer.success_tone()
                        time.sleep(2)  # Show Hello for 2 seconds
                        
                        # Then show ArUco instruction
                        self.lcd.display_message("Show ArUco", f"Code: {aruco_id}")
                        
                        current_state = STATE_WAITING_ARUCO
                        state_start_time = current_time
                    else:
                        # Face not recognized
                        print("[Attendance] Face not recognized")
                        cv2.putText(frame, "Not recognized", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        
                        elapsed = current_time - state_start_time
                        if elapsed > 5.0:
                            self.lcd.display_message("Unknown Face", "Not enrolled")
                            self.buzzer.error_tone()
                            current_state = STATE_WAITING
                            time.sleep(2)
                    
                    if HARDWARE_MODE == "PC":
                        cv2.imshow("Attendance System", frame)
                        key = cv2.waitKey(100) & 0xFF
                        if key == ord('q'):
                            break
                
                # ===== STATE: WAITING FOR ARUCO =====
                elif current_state == STATE_WAITING_ARUCO:
                    elapsed = current_time - state_start_time
                    remaining = max(0, 3 - int(elapsed))
                    
                    self.lcd.display_message("Show ArUco", f"Code: {recognized_student['aruco_id']}")
                    
                    frame = self.capture_multi_frame(num_frames=5)
                    if frame is not None:
                        cv2.putText(frame, f"Hello {recognized_student['name']}!", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Show ArUco marker (ID: {recognized_student['aruco_id']})", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        cv2.putText(frame, f"Starting in {remaining}s...", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                        
                        if HARDWARE_MODE == "PC":
                            cv2.imshow("Attendance System", frame)
                            key = cv2.waitKey(100) & 0xFF
                            if key == ord('q'):
                                break
                    
                    if elapsed >= 3.0:
                        current_state = STATE_DETECTING_ARUCO
                        state_start_time = current_time
                        print("[Attendance] Starting ArUco detection...")
                        self.lcd.display_message("Detecting", "ArUco...")
                
                # ===== STATE: DETECTING ARUCO =====
                elif current_state == STATE_DETECTING_ARUCO:
                    elapsed = current_time - state_start_time
                    
                    self.lcd.display_message("Scanning", "ArUco Code...")
                    
                    frame = self.capture_multi_frame(num_frames=10)
                    if frame is None:
                        continue
                    
                    # Detect ArUco
                    marker_ids, corners = self.aruco_detector.detect_markers(frame)
                    
                    if len(marker_ids) > 0:
                        # Draw detected markers
                        frame = self.aruco_detector.draw_markers(frame, corners, marker_ids)
                        cv2.putText(frame, f"Detected: {marker_ids}", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Check if expected ArUco detected
                        expected_id = recognized_student['aruco_id']
                        
                        if expected_id in marker_ids:
                            # ArUco matches! Check if already marked today
                            if self.db.check_attendance_today(recognized_student['id']):
                                print(f"[Attendance] {recognized_student['name']} already marked today!")
                                self.lcd.display_message("Already", "Marked Today!")
                                self.buzzer.warning_tone()
                                current_state = STATE_WAITING
                                time.sleep(3)
                                continue
                            
                            # Mark attendance
                            success = self.db.mark_attendance(recognized_student['id'])
                            
                            if success:
                                print(f"\n{'='*50}")
                                print(f"✓ ATTENDANCE MARKED: {recognized_student['name']}")
                                print(f"  ArUco ID: {expected_id}")
                                print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
                                print(f"{'='*50}\n")
                                
                                # Play success tone immediately
                                self.lcd.display_message("ATTENDANCE", "MARKED!")
                                self.buzzer.success_tone()
                                
                                current_state = STATE_SUCCESS
                                state_start_time = current_time
                            else:
                                print("[Attendance] Database error!")
                                self.lcd.display_message("Database", "Error!")
                                self.buzzer.error_tone()
                                current_state = STATE_WAITING
                                time.sleep(2)
                        else:
                            # Wrong ArUco
                            print(f"[Attendance] Wrong ArUco! Expected {expected_id}, got {marker_ids}")
                            cv2.putText(frame, f"Wrong ArUco! Expected: {expected_id}", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            self.lcd.display_message("ArUco Wrong!", f"Need: {expected_id}")
                            self.buzzer.error_tone()
                    else:
                        cv2.putText(frame, "Show ArUco marker to camera", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        cv2.putText(frame, f"Expected ID: {recognized_student['aruco_id']}", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                    
                    # Timeout after 10 seconds
                    if elapsed > 10.0:
                        print("[Attendance] ArUco timeout")
                        self.lcd.display_message("ArUco", "Timeout!")
                        self.buzzer.error_tone()
                        current_state = STATE_WAITING
                        recognized_student = None
                        time.sleep(2)
                    
                    if HARDWARE_MODE == "PC":
                        cv2.imshow("Attendance System", frame)
                        key = cv2.waitKey(100) & 0xFF
                        if key == ord('q'):
                            break
                
                # ===== STATE: SUCCESS =====
                elif current_state == STATE_SUCCESS:
                    elapsed = current_time - state_start_time
                    
                    frame = self.capture_multi_frame(num_frames=5)
                    if frame is not None:
                        cv2.putText(frame, "ATTENDANCE MARKED!", (10, 50),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                        cv2.putText(frame, f"{recognized_student['name']}", (10, 100),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                        cv2.putText(frame, f"ArUco ID: {recognized_student['aruco_id']}", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        
                        if HARDWARE_MODE == "PC":
                            cv2.imshow("Attendance System", frame)
                            cv2.waitKey(100)
                    
                    if elapsed >= 5.0:
                        print("[Attendance] Ready for next student")
                        self.lcd.display_message("Ready", "Next student")
                        current_state = STATE_WAITING
                        recognized_student = None
                    else:
                        time.sleep(0.5)
                
                # ===== STATE: ERROR =====
                elif current_state == STATE_ERROR:
                    elapsed = current_time - state_start_time
                    
                    if elapsed >= 3.0:
                        current_state = STATE_WAITING
                        recognized_student = None
                        self.lcd.display_message("Ready", "Show your face")
                    else:
                        time.sleep(0.5)
                    
        except KeyboardInterrupt:
            print("\n[Exit] Interrupted by user")
            
        finally:
            self.cleanup()
            
    def show_statistics(self):
        """Display attendance statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        attendance_records = self.db.get_attendance_by_date(today)
        
        print("\n" + "="*50)
        print(f"ATTENDANCE STATISTICS - {today}")
        print("="*50)
        print(f"Total students enrolled: {self.db.get_student_count()}")
        print(f"Students present today: {len(attendance_records)}")
        print("\nAttendance Records:")
        
        if attendance_records:
            for name, time_str, status in attendance_records:
                print(f"  - {name}: {time_str} ({status})")
        else:
            print("  No attendance marked yet today")
            
        print("="*50 + "\n")
        
    def cleanup(self):
        """Clean up all resources"""
        print("\n[Cleanup] Releasing resources...")
        
        try:
            self.camera.release()
            self.ultrasonic1.cleanup()
            self.ultrasonic2.cleanup()
            self.lcd.cleanup()
            self.buzzer.cleanup()
            
            if HARDWARE_MODE == "PC":
                cv2.destroyAllWindows()
                
        except Exception as e:
            print(f"[Cleanup] Error during cleanup: {e}")
            
        print("[Cleanup] System shutdown complete")


def main():
    """Main entry point"""
    try:
        system = AttendanceSystem()
        system.run()
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

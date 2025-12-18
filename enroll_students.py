"""
Student Enrollment Script
One-time enrollment of students with face and ArUco tag registration
"""
import cv2
import sys
import os
import time
from datetime import datetime

# Import configuration
from config import *

# Import modules
from database.db_manager import DatabaseManager
from ai.face_detector import FaceDetector
from ai.face_recognition import FaceRecognizer
from ai.aruco_detector import ArucoDetector
from hardware.camera import Camera
from hardware.lcd import LCDDisplay
from hardware.buzzer import Buzzer


class EnrollmentSystem:
    """Student enrollment system for one-time registration"""
    
    def __init__(self):
        """Initialize enrollment system"""
        print("="*50)
        print("STUDENT ENROLLMENT SYSTEM")
        print("="*50)
        print(f"Hardware Mode: {HARDWARE_MODE}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Initialize hardware based on mode
        self.use_lcd = (HARDWARE_MODE == "RASPBERRY_PI")
        
        # Initialize camera
        print("\n[Init] Initializing camera...")
        self.camera = Camera(
            mode=HARDWARE_MODE,
            camera_index=CAMERA_INDEX,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT
        )
        
        # Camera warmup - capture a few frames to stabilize
        print("[Init] Warming up camera...")
        for _ in range(10):
            self.camera.read_frame()
            time.sleep(0.1)
        print("[Init] Camera ready!")
        
        # Initialize LCD and Buzzer for Raspberry Pi
        if self.use_lcd:
            print("[Init] Initializing LCD...")
            self.lcd = LCDDisplay(mode=HARDWARE_MODE, i2c_address=LCD_I2C_ADDRESS)
            print("[Init] Initializing Buzzer...")
            self.buzzer = Buzzer(mode=HARDWARE_MODE, pin=BUZZER_PIN)
            # Show ready message on LCD
            self.lcd.display_message("Enrollment", "System Ready")
        else:
            self.lcd = None
            self.buzzer = None
        
        # Initialize AI modules
        print("[Init] Initializing AI modules...")
        self.face_detector = FaceDetector(backend=FACE_DETECTION_BACKEND)
        self.face_recognizer = FaceRecognizer(model_name=FACE_MODEL, backend=FACE_DETECTION_BACKEND)
        self.aruco_detector = ArucoDetector(dictionary=ARUCO_DICT)
        
        # Initialize database
        print("[Init] Connecting to database...")
        self.db = DatabaseManager(DATABASE_PATH)
        
        print("\n[Init] Enrollment system ready!")
        
    def capture_face_embedding(self, student_name):
        """
        Capture face and generate embedding using multi-frame capture
        
        Args:
            student_name: Name of student
            
        Returns:
            Face embedding or None
        """
        print(f"\n[Capture] Capturing face for: {student_name}")
        
        # Step 1: Show initial instruction on LCD
        if self.lcd:
            self.lcd.display_message("Put Your Face", "In front camera")
        print("[Capture] Position your face in front of the camera...")
        print("[Capture] Waiting 5 seconds...")
        time.sleep(5)  # Give user time to position
        
        # Step 2: Capture multiple frames
        if self.lcd:
            self.lcd.display_message("Capturing...", "Hold still!")
        print("[Capture] Capturing frames...")
        
        frames_to_capture = 15
        captured_frames = []
        retry_count = 0
        max_retries = 60  # Max attempts to get frames (increased)
        
        while len(captured_frames) < frames_to_capture and retry_count < max_retries:
            frame = self.camera.read_frame()
            retry_count += 1
            
            if frame is None:
                print(f"[Capture] Frame {retry_count}: None (retrying...)")
                time.sleep(0.2)
                continue
            
            captured_frames.append(frame.copy())
            print(f"[Capture] Captured frame {len(captured_frames)}/{frames_to_capture}")
            if self.lcd:
                self.lcd.display_message("Capturing...", f"Frame {len(captured_frames)}/{frames_to_capture}")
            time.sleep(0.2)  # Delay between frames
        
        if len(captured_frames) < 5:
            print(f"[Error] Could not capture enough frames (got {len(captured_frames)}, need at least 5)")
            print("[Error] Check camera connection or try: rpicam-hello")
            if self.lcd:
                self.lcd.display_message("Camera Error", "Check connection")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(3)
            return None
        
        print(f"[Capture] Got {len(captured_frames)} frames, analyzing...")
        
        # Step 3: Find the best frame with a single face
        if self.lcd:
            self.lcd.display_message("Analyzing...", "Finding best")
        
        best_frame = None
        best_face_size = 0
        
        for frame in captured_frames:
            faces = self.face_detector.detect_faces(frame)
            
            if len(faces) == 1:
                # Calculate face size (larger = better quality)
                x, y, w, h = faces[0]
                face_size = w * h
                
                if face_size > best_face_size:
                    best_face_size = face_size
                    best_frame = frame
        
        if best_frame is None:
            print("[Capture] No single face detected in any frame")
            if self.lcd:
                self.lcd.display_message("No Face Found", "Try again")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(2)
            return None
        
        print(f"[Capture] Best face found (size: {best_face_size})")
        
        # Step 4: Extract face and generate embedding
        if self.lcd:
            self.lcd.display_message("Processing...", "Analyzing face")
        
        face_roi, face_bbox = self.face_detector.get_single_face(best_frame)
        
        if face_roi is None:
            print("[Capture] Failed to extract face from best frame")
            if self.lcd:
                self.lcd.display_message("Error", "Face unclear")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(2)
            return None
        
        # Generate embedding
        print("[Capture] Generating face embedding...")
        face_embedding = self.face_recognizer.generate_embedding(face_roi)
        
        if face_embedding is not None:
            print("[Capture] ✓ Face embedding generated successfully!")
            if self.lcd:
                self.lcd.display_message("Success!", "Face captured")
            if self.buzzer:
                self.buzzer.success()
            time.sleep(2)
            return face_embedding
        else:
            print("[Capture] ✗ Failed to generate embedding")
            if self.lcd:
                self.lcd.display_message("Error", "Try again")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(2)
            return None
        
    def capture_aruco_id(self, student_name):
        """
        Capture ArUco marker ID using multi-frame capture
        
        Args:
            student_name: Name of student
            
        Returns:
            ArUco ID or None
        """
        print(f"\n[Capture] Capturing ArUco marker for: {student_name}")
        
        # Step 1: Show initial instruction on LCD
        if self.lcd:
            self.lcd.display_message("Show ArUco", "Marker to camera")
        print("[Capture] Show the ArUco marker to the camera...")
        print("[Capture] Waiting 5 seconds...")
        time.sleep(5)  # Give user time to position marker
        
        # Step 2: Capture multiple frames
        if self.lcd:
            self.lcd.display_message("Capturing...", "Hold steady!")
        print("[Capture] Capturing frames...")
        
        frames_to_capture = 15
        captured_frames = []
        retry_count = 0
        max_retries = 60  # Increased
        
        while len(captured_frames) < frames_to_capture and retry_count < max_retries:
            frame = self.camera.read_frame()
            retry_count += 1
            
            if frame is None:
                print(f"[Capture] Frame {retry_count}: None (retrying...)")
                time.sleep(0.2)
                continue
            
            captured_frames.append(frame.copy())
            print(f"[Capture] Captured frame {len(captured_frames)}/{frames_to_capture}")
            if self.lcd:
                self.lcd.display_message("Capturing...", f"Frame {len(captured_frames)}/{frames_to_capture}")
            time.sleep(0.2)
        
        if len(captured_frames) < 5:
            print(f"[Error] Could not capture enough frames (got {len(captured_frames)}, need at least 5)")
            print("[Error] Check camera connection or try: rpicam-hello")
            if self.lcd:
                self.lcd.display_message("Camera Error", "Check connection")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(3)
            return None
        
        print(f"[Capture] Got {len(captured_frames)} frames, analyzing...")
        
        # Step 3: Find best frame with a single ArUco marker
        if self.lcd:
            self.lcd.display_message("Analyzing...", "Finding marker")
        
        # Count detected marker IDs across all frames
        marker_counts = {}
        
        for frame in captured_frames:
            marker_ids, corners = self.aruco_detector.detect_markers(frame)
            
            if len(marker_ids) == 1:
                marker_id = marker_ids[0]
                marker_counts[marker_id] = marker_counts.get(marker_id, 0) + 1
        
        if not marker_counts:
            print("[Capture] No ArUco marker detected in any frame")
            if self.lcd:
                self.lcd.display_message("No Marker", "Try again")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(2)
            return None
        
        # Get the most frequently detected marker
        best_marker_id = max(marker_counts, key=marker_counts.get)
        detection_count = marker_counts[best_marker_id]
        
        print(f"[Capture] Marker {best_marker_id} detected {detection_count} times")
        
        if detection_count < 3:
            print("[Capture] Marker not stable enough, try again")
            if self.lcd:
                self.lcd.display_message("Marker unclear", "Try again")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(2)
            return None
        
        # Success!
        print(f"[Capture] ✓ ArUco marker captured: ID {best_marker_id}")
        if self.lcd:
            self.lcd.display_message("Success!", f"Marker: {best_marker_id}")
        if self.buzzer:
            self.buzzer.success()
        time.sleep(2)
        
        return best_marker_id
        
    def enroll_student(self, name, aruco_id, face_embedding):
        """
        Enroll student in database
        
        Args:
            name: Student name
            aruco_id: ArUco marker ID
            face_embedding: Face embedding vector
            
        Returns:
            Student ID if successful, None otherwise
        """
        print(f"\n[Enroll] Enrolling student: {name}")
        print(f"[Enroll] ArUco ID: {aruco_id}")
        
        if self.lcd:
            self.lcd.display_message("Saving...", "Please wait")
        
        student_id = self.db.add_student(name, aruco_id, face_embedding)
        
        if student_id:
            print(f"[Enroll] ✓ Student enrolled successfully! ID: {student_id}")
            if self.lcd:
                self.lcd.display_message("Enrolled!", f"{name}")
            if self.buzzer:
                self.buzzer.success()
                time.sleep(0.2)
                self.buzzer.success()
            time.sleep(3)
            return student_id
        else:
            print("[Enroll] ✗ Failed to enroll student (ArUco ID may already exist)")
            if self.lcd:
                self.lcd.display_message("Error", "ID exists")
            if self.buzzer:
                self.buzzer.error()
            time.sleep(3)
            return None
            
    def run_enrollment(self):
        """Run interactive enrollment process"""
        print("\n" + "="*50)
        print("STARTING ENROLLMENT PROCESS")
        print("="*50)
        
        enrolled_count = 0
        
        try:
            while True:
                print("\n" + "-"*50)
                student_name = input("\nEnter student name (or 'quit' to exit): ").strip()
                
                if student_name.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not student_name:
                    print("[Error] Name cannot be empty")
                    continue
                    
                # Capture face embedding
                face_embedding = self.capture_face_embedding(student_name)
                
                if face_embedding is None:
                    print("[Enroll] Skipping student due to cancelled face capture")
                    continue
                    
                # Capture ArUco ID
                aruco_id = self.capture_aruco_id(student_name)
                
                if aruco_id is None:
                    print("[Enroll] Skipping student due to cancelled ArUco capture")
                    continue
                    
                # Enroll in database
                student_id = self.enroll_student(student_name, aruco_id, face_embedding)
                
                if student_id:
                    enrolled_count += 1
                    print(f"\n✓ {student_name} enrolled successfully!")
                else:
                    print(f"\n✗ Failed to enroll {student_name}")
                    
        except KeyboardInterrupt:
            print("\n[Exit] Interrupted by user")
            
        finally:
            self.cleanup()
            
        print("\n" + "="*50)
        print(f"ENROLLMENT COMPLETE")
        print(f"Total students enrolled: {enrolled_count}")
        print("="*50)
        
    def generate_aruco_markers(self, start_id=0, count=50):
        """
        Generate ArUco markers for printing
        
        Args:
            start_id: Starting marker ID
            count: Number of markers to generate
        """
        print(f"\n[Generator] Generating {count} ArUco markers...")
        
        output_dir = os.path.join(BASE_DIR, "aruco_markers")
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(count):
            marker_id = start_id + i
            marker_img = self.aruco_detector.generate_marker(marker_id, size=200)
            
            filename = os.path.join(output_dir, f"aruco_marker_{marker_id}.png")
            cv2.imwrite(filename, marker_img)
            
        print(f"[Generator] ✓ Generated {count} markers in: {output_dir}")
        print(f"[Generator] Print these markers for student enrollment")
        
    def cleanup(self):
        """Clean up resources"""
        print("\n[Cleanup] Releasing resources...")
        self.camera.release()
        if not self.use_lcd:
            cv2.destroyAllWindows()
        if self.lcd:
            self.lcd.clear()
        print("[Cleanup] Cleanup complete")


def main():
    """Main entry point"""
    print("\n1. Enroll students")
    print("2. Generate ArUco markers")
    print("3. View enrolled students")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    try:
        if choice == "1":
            system = EnrollmentSystem()
            system.run_enrollment()
            
        elif choice == "2":
            system = EnrollmentSystem()
            start_id = int(input("Starting marker ID (default 0): ").strip() or "0")
            count = int(input("Number of markers (default 50): ").strip() or "50")
            system.generate_aruco_markers(start_id, count)
            system.cleanup()
            
        elif choice == "3":
            db = DatabaseManager(DATABASE_PATH)
            students = db.get_all_students()
            
            print("\n" + "="*50)
            print("ENROLLED STUDENTS")
            print("="*50)
            
            if students:
                for student_id, name, aruco_id, _ in students:
                    print(f"ID: {student_id} | Name: {name} | ArUco: {aruco_id}")
            else:
                print("No students enrolled yet")
                
            print("="*50)
            
        else:
            print("Invalid option")
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

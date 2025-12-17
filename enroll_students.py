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
        
        # Initialize camera
        print("\n[Init] Initializing camera...")
        self.camera = Camera(
            mode=HARDWARE_MODE,
            camera_index=CAMERA_INDEX,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT
        )
        
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
        Capture face and generate embedding
        
        Args:
            student_name: Name of student
            
        Returns:
            Face embedding or None
        """
        print(f"\n[Capture] Capturing face for: {student_name}")
        print("[Capture] Position your face in front of the camera...")
        print("[Capture] Press SPACE to capture, ESC to cancel")
        
        captured = False
        face_embedding = None
        
        while not captured:
            frame = self.camera.read_frame()
            
            if frame is None:
                print("[Error] Failed to read frame")
                time.sleep(0.1)
                continue
                
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            display_frame = self.face_detector.draw_faces(frame, faces)
            
            # Show status
            if len(faces) == 0:
                status = "No face detected"
                color = (0, 0, 255)
            elif len(faces) == 1:
                status = "Ready! Press SPACE to capture"
                color = (0, 255, 0)
            else:
                status = "Multiple faces! Only one person"
                color = (0, 0, 255)
                
            cv2.putText(display_frame, status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(display_frame, f"Enrolling: {student_name}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Enrollment - Face Capture", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and len(faces) == 1:
                # Capture face
                face_roi, face_bbox = self.face_detector.get_single_face(frame)
                
                if face_roi is not None:
                    # Quality check removed - proceed directly to embedding generation
                    print("[Capture] Face captured! Generating embedding...")
                    
                    # Generate embedding
                    face_embedding = self.face_recognizer.generate_embedding(face_roi)
                    
                    if face_embedding is not None:
                        print("[Capture] ✓ Face embedding generated successfully!")
                        captured = True
                    else:
                        print("[Capture] ✗ Failed to generate embedding. Try again.")
                else:
                    print("[Capture] ✗ Failed to extract face. Try again.")
                    
            elif key == 27:  # ESC
                print("[Capture] Cancelled by user")
                return None
                
        return face_embedding
        
    def capture_aruco_id(self, student_name):
        """
        Capture ArUco marker ID
        
        Args:
            student_name: Name of student
            
        Returns:
            ArUco ID or None
        """
        print(f"\n[Capture] Capturing ArUco marker for: {student_name}")
        print("[Capture] Show the ArUco marker to the camera...")
        print("[Capture] Press SPACE to capture, ESC to cancel")
        
        captured = False
        aruco_id = None
        
        while not captured:
            frame = self.camera.read_frame()
            
            if frame is None:
                print("[Error] Failed to read frame")
                time.sleep(0.1)
                continue
                
            # Detect ArUco markers
            marker_ids, corners = self.aruco_detector.detect_markers(frame)
            display_frame = self.aruco_detector.draw_markers(frame, corners, marker_ids)
            
            # Show status
            if len(marker_ids) == 0:
                status = "No ArUco marker detected"
                color = (0, 0, 255)
            elif len(marker_ids) == 1:
                status = f"Marker ID: {marker_ids[0]} - Press SPACE"
                color = (0, 255, 0)
            else:
                status = "Multiple markers! Show only one"
                color = (0, 0, 255)
                
            cv2.putText(display_frame, status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(display_frame, f"Enrolling: {student_name}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Enrollment - ArUco Capture", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and len(marker_ids) == 1:
                # Capture ArUco ID
                aruco_id = marker_ids[0]
                print(f"[Capture] ✓ ArUco marker captured: ID {aruco_id}")
                captured = True
                
            elif key == 27:  # ESC
                print("[Capture] Cancelled by user")
                return None
                
        return aruco_id
        
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
        
        student_id = self.db.add_student(name, aruco_id, face_embedding)
        
        if student_id:
            print(f"[Enroll] ✓ Student enrolled successfully! ID: {student_id}")
            return student_id
        else:
            print("[Enroll] ✗ Failed to enroll student (ArUco ID may already exist)")
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
        cv2.destroyAllWindows()
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

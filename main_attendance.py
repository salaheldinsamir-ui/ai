"""
Main Attendance System Program
Auto-starts on boot and continuously checks attendance
"""
import cv2
import sys
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
from hardware.ultrasonic import UltrasonicSensor
from hardware.lcd import LCDDisplay
from hardware.buzzer import Buzzer
from attendance_engine import AttendanceEngine


class AttendanceSystem:
    """Main attendance system application"""
    
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
        
        self.lcd = LCDDisplay(
            mode=HARDWARE_MODE,
            i2c_address=LCD_I2C_ADDRESS,
            rows=LCD_ROWS,
            cols=LCD_COLS
        )
        
        self.buzzer = Buzzer(
            mode=HARDWARE_MODE,
            pin=BUZZER_PIN
        )
        
        # Initialize AI modules
        print("\n[Init] Initializing AI modules...")
        self.face_detector = FaceDetector(backend=FACE_DETECTION_BACKEND)
        self.face_recognizer = FaceRecognizer(model_name=FACE_MODEL, backend=FACE_DETECTION_BACKEND)
        self.aruco_detector = ArucoDetector(dictionary=ARUCO_DICT)
        
        # Initialize database
        print("\n[Init] Connecting to database...")
        self.db = DatabaseManager(DATABASE_PATH)
        student_count = self.db.get_student_count()
        print(f"[Init] Database loaded: {student_count} students enrolled")
        
        if student_count == 0:
            print("\n[Warning] No students enrolled! Please run enroll_students.py first.")
            self.lcd.display_message("No Students", "Enrolled!")
            time.sleep(3)
            
        # Initialize attendance engine
        print("\n[Init] Initializing attendance engine...")
        self.engine = AttendanceEngine(
            db_manager=self.db,
            face_detector=self.face_detector,
            face_recognizer=self.face_recognizer,
            aruco_detector=self.aruco_detector,
            ultrasonic_sensor1=self.ultrasonic1,
            ultrasonic_sensor2=self.ultrasonic2,
            lcd=self.lcd,
            buzzer=self.buzzer,
            threshold=FACE_RECOGNITION_THRESHOLD
        )
        
        print("\n[Init] System initialization complete!")
        self.lcd.display_welcome()
        self.buzzer.success_tone()
        
    def run(self):
        """Main attendance checking loop"""
        print("\n" + "="*50)
        print("ATTENDANCE SYSTEM ACTIVE")
        print("Press 'q' to quit, 's' to show stats")
        print("="*50 + "\n")
        
        frame_count = 0
        
        try:
            while True:
                # Read frame from camera
                frame = self.camera.read_frame()
                
                if frame is None:
                    print("[Error] Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                    
                frame_count += 1
                
                # Check presence first
                if not self.engine.check_presence():
                    # No presence detected - show waiting frame
                    display_frame = frame.copy()
                    cv2.putText(display_frame, "Waiting for person...", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    if HARDWARE_MODE == "PC":
                        cv2.imshow("Attendance System", display_frame)
                    
                    # Handle keyboard input
                    if HARDWARE_MODE == "PC":
                        key = cv2.waitKey(10) & 0xFF
                        if key == ord('q'):
                            print("\n[Exit] Shutting down system...")
                            break
                        elif key == ord('s'):
                            self.show_statistics()
                    else:
                        time.sleep(0.1)
                    
                    continue
                
                # Process frame for attendance (continuous processing)
                success, message, processed_frame = self.engine.run_attendance_check(frame)
                
                # Display processed frame
                if HARDWARE_MODE == "PC":
                    cv2.imshow("Attendance System", processed_frame)
                
                # Handle different states and update LCD
                if message == "idle":
                    # System in standby
                    self.lcd.display_message("System", "Standby Mode")
                
                elif message == "entering_idle":
                    # Going to idle mode
                    print(f"\n[System] Entering standby mode")
                    self.lcd.display_message("System", "Standby Mode")
                
                elif message == "waiting_for_stable_face":
                    # Waiting for face to stabilize
                    self.lcd.display_message("Hold Still", "Please...")
                
                elif message == "start_detecting_face":
                    # Starting face recognition
                    self.lcd.display_message("Recognizing", "Face...")
                
                elif message == "face_recognized":
                    # Face recognized, waiting for ArUco
                    student_name = self.engine.recognized_student['name']
                    self.lcd.display_message("Hello", student_name[:16])
                
                elif message == "waiting_aruco_instruction":
                    # Waiting for ArUco marker
                    self.lcd.display_message("Show ArUco", "Marker")
                
                elif message == "start_detecting_aruco":
                    # Starting ArUco detection
                    self.lcd.display_message("Detecting", "ArUco...")
                
                elif message == "aruco_detected":
                    print(f"\n→ ArUco detected - showing ID for 1 second...")
                    self.lcd.display_message("ArUco", "Detected!")
                
                elif message == "showing_aruco_id":
                    # Just keep displaying
                    pass
                
                # Handle success (after ArUco display)
                elif success:
                    # Attendance marked successfully
                    student_name, aruco_id = message
                    print(f"\n✓ {student_name} - Attended (ArUco ID: {aruco_id})")
                    print(f"   Displaying confirmation for 5 seconds...")
                    self.lcd.display_message("Attendance", "Taken!")
                    self.buzzer.success_tone()
                
                # Success message being displayed
                elif message == "showing_success":
                    # Keep showing attendance taken
                    pass
                
                # Success display period ended
                elif message == "success_displayed":
                    print(f"   ✓ Confirmation displayed - Ready for next student")
                    self.lcd.display_message("Attendance", "System Ready")
                
                # Handle errors
                elif message == "aruco_timeout":
                    print(f"\n✗ ERROR: Cannot read ArUco code - Please try again")
                    print(f"   Displaying error for 3 seconds...")
                    self.lcd.display_error("no_aruco")
                    self.buzzer.error_tone()
                
                elif message == "not_recognized":
                    self.lcd.display_error("not_recognized")
                    self.buzzer.error_tone()
                
                elif message == "mismatch":
                    self.lcd.display_error("mismatch")
                    self.buzzer.error_tone()
                
                elif message == "already_marked":
                    self.lcd.display_error("already_marked")
                    self.buzzer.error_tone()
                
                # Error message being displayed
                elif message == "showing_error":
                    # Just keep displaying
                    pass
                
                # Error display period ended
                elif message == "error_displayed":
                    print(f"   Error displayed - Restarting...")
                    self.lcd.display_message("Attendance", "System Ready")
                        
                # Handle keyboard input (PC mode)
                if HARDWARE_MODE == "PC":
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        print("\n[Exit] Shutting down system...")
                        break
                        
                    elif key == ord('s'):
                        self.show_statistics()
                        
                else:
                    # Small delay for Raspberry Pi
                    time.sleep(0.1)
                    
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

"""
Configuration file for the attendance system
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

# Camera configuration
CAMERA_INDEX = 0  # 0 for PC webcam, will be different for Pi Camera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Face recognition configuration
FACE_RECOGNITION_THRESHOLD = 0.6  # Cosine similarity threshold (0-1)
FACE_MODEL = "Facenet"  # Options: "Facenet", "VGG-Face", "OpenFace"
FACE_DETECTION_BACKEND = "opencv"  # Options: "opencv", "ssd", "dlib", "mtcnn", "retinaface"

# Face quality validation (lower = more lenient for poor lighting)
MIN_BRIGHTNESS = 20  # Minimum average brightness (0-255, default: 20)
MIN_CONTRAST = 10    # Minimum contrast/standard deviation (default: 10)
MIN_SHARPNESS = 50   # Minimum sharpness/Laplacian variance (default: 50)

# ArUco configuration
ARUCO_DICT = "DICT_4X4_50"  # ArUco dictionary type

# Ultrasonic sensor configuration (Raspberry Pi only)
ULTRASONIC_SENSOR_1_TRIGGER = 23
ULTRASONIC_SENSOR_1_ECHO = 24
ULTRASONIC_SENSOR_2_TRIGGER = 27
ULTRASONIC_SENSOR_2_ECHO = 22

# Distance thresholds (in cm)
MIN_DISTANCE = 30  # Minimum distance to activate
MAX_DISTANCE = 100  # Maximum distance to activate

# LCD configuration (Raspberry Pi only)
LCD_I2C_ADDRESS = 0x27
LCD_ROWS = 2
LCD_COLS = 16

# Buzzer configuration (Raspberry Pi only)
BUZZER_PIN = 17

# Hardware mode
HARDWARE_MODE = "PC"  # Options: "PC", "RASPBERRY_PI"

# Attendance settings
DUPLICATE_ATTENDANCE_WINDOW = 86400  # Seconds in a day (prevents duplicate attendance on same day)

# Logging configuration
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_FILE = os.path.join(BASE_DIR, "attendance.log")

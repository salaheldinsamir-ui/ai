"""
Quick Start Guide - Run this first!
"""

print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     AI-POWERED ATTENDANCE SYSTEM - QUICK START GUIDE          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📋 SETUP STEPS:

1. Install Dependencies
   ────────────────────
   pip install -r requirements.txt
   
   This will install:
   • OpenCV (computer vision)
   • DeepFace (face recognition)
   • TensorFlow (deep learning)
   • Other required packages

2. Test Your Setup
   ────────────────
   python test_setup.py
   
   This verifies:
   • All packages are installed
   • Camera is working
   • Database can be created
   • AI modules are functional

3. Generate ArUco Markers (One-time)
   ──────────────────────────────────
   python enroll_students.py
   → Select option 2: Generate ArUco markers
   → Print the markers from aruco_markers/ folder
   → Assign one marker to each student

4. Enroll Students (One-time)
   ──────────────────────────
   python enroll_students.py
   → Select option 1: Enroll students
   → For each student:
     • Enter name
     • Capture face (press SPACE)
     • Show ArUco marker (press SPACE)

5. Run Attendance System
   ─────────────────────
   python main_attendance.py
   
   The system will:
   • Display camera feed (PC mode)
   • Check for face + ArUco markers
   • Mark attendance automatically
   • Show results on screen/LCD

📊 VIEW ATTENDANCE:

   • Press 'S' during operation to see statistics
   • View database: attendance_system/database/attendance.db
   • Check enrolled students: python enroll_students.py → option 3

⚙️ CONFIGURATION:

   Edit config.py to customize:
   • Face recognition threshold
   • Camera settings
   • Hardware mode (PC/Raspberry Pi)
   • Distance thresholds

🔧 RASPBERRY PI DEPLOYMENT:

   After testing on PC:
   1. Copy entire folder to Raspberry Pi
   2. Install Pi-specific libraries:
      sudo apt-get install python3-picamera2
      pip install RPi.GPIO RPLCD
   3. Edit config.py: HARDWARE_MODE = "RASPBERRY_PI"
   4. Connect hardware (camera, sensors, LCD, buzzer)
   5. Run: python main_attendance.py

📚 DOCUMENTATION:

   • Full documentation: README.md
   • Configuration: config.py
   • Troubleshooting: README.md → Troubleshooting section

🎯 KEY FEATURES:

   ✓ Dual authentication (face + ArUco)
   ✓ Anti-spoofing (ultrasonic sensors)
   ✓ One-time enrollment
   ✓ Automatic duplicate prevention
   ✓ PC and Raspberry Pi support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 RECOMMENDED ORDER:

   1. pip install -r requirements.txt
   2. python test_setup.py
   3. python enroll_students.py (option 2 → option 1)
   4. python main_attendance.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need help? Check README.md for detailed instructions!

""")

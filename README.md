# 📋 Smart Attendance System - Complete Guide

A Raspberry Pi-based attendance system using **face recognition** and **ArUco markers** for accurate student identification. Features a modern web UI accessible from any phone or device.

## 📸 Screenshots

### Web Interface
![AI Attendance System Interface 1](screenshots/AI%201.png)
![AI Attendance System Interface 2](screenshots/AI%202.png)

---

## 📑 Table of Contents

1. [System Overview](#system-overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Requirements](#software-requirements)
4. [Installation](#installation)
5. [Database Schema](#database-schema)
6. [Web UI Guide](#web-ui-guide)
7. [WiFi Hotspot Setup](#wifi-hotspot-setup)
8. [Running the System](#running-the-system)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

### How It Works

1. **Student Enrollment**: Each student registers with:

   - Their face (for face recognition)
   - A unique ArUco marker ID (for quick identification)

2. **Attendance Tracking**: When taking attendance:

   - Student shows ArUco marker to camera
   - System detects marker and identifies student
   - Face verification confirms identity
   - Attendance is recorded with timestamp

3. **Web Management**: Access via phone/browser to:
   - Enroll new students
   - View attendance records
   - Manage student database
   - Control system settings

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Camera     │  │  Ultrasonic  │  │    LCD       │       │
│  │  (Pi Camera) │  │   Sensor     │  │  Display     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────▼─────────────────▼─────────────────▼───────┐       │
│  │              ATTENDANCE ENGINE                     │       │
│  │  • Face Detection (OpenCV/DeepFace)               │       │
│  │  • ArUco Marker Detection                          │       │
│  │  • Face Recognition & Matching                     │       │
│  └──────────────────────┬───────────────────────────┘       │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────┐       │
│  │              SQLite DATABASE                       │       │
│  │  • Students (name, aruco_id, face_embedding)      │       │
│  │  • Attendance (student_id, date, time, status)    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              WEB MANAGER (Flask)                   │       │
│  │  • Port 4000                                       │       │
│  │  • Mobile-friendly UI                              │       │
│  │  • Enrollment, Attendance View, Settings          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │
         │ WiFi / Hotspot
         ▼
    ┌─────────────┐
    │   Phone     │
    │   Browser   │
    │ 192.168.x.x │
    └─────────────┘
```

---

## 🔧 Hardware Requirements

| Component                   | Description         | Connection |
| --------------------------- | ------------------- | ---------- |
| Raspberry Pi 4/5            | Main controller     | -          |
| Pi Camera Module            | Face/ArUco capture  | CSI port   |
| Ultrasonic Sensor (HC-SR04) | Proximity detection | GPIO       |
| I2C LCD Display (16x2)      | Status display      | I2C        |
| Buzzer                      | Audio feedback      | GPIO       |
| Power Supply                | 5V 3A               | USB-C      |

### GPIO Pin Configuration

```
┌─────────────────────────────────────────┐
│           RASPBERRY PI GPIO             │
├─────────────────────────────────────────┤
│                                         │
│  Ultrasonic Sensor (HC-SR04):           │
│    • TRIG → GPIO 23                     │
│    • ECHO → GPIO 24                     │
│    • VCC  → 5V                          │
│    • GND  → GND                         │
│                                         │
│  Buzzer:                                │
│    • Signal → GPIO 18                   │
│    • GND    → GND                       │
│                                         │
│  LCD Display (I2C):                     │
│    • SDA → GPIO 2 (SDA)                 │
│    • SCL → GPIO 3 (SCL)                 │
│    • VCC → 5V                           │
│    • GND → GND                          │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💻 Software Requirements

- **Raspberry Pi OS** (64-bit recommended)
- **Python 3.9+**
- **OpenCV** with ArUco support
- **DeepFace** for face recognition
- **Flask** for web UI

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
cd ~
git clone https://github.com/salaheldinsamir-ui/ai.git
cd ai
```

### Step 2: Run the Setup Script

```bash
chmod +x install_raspberry.sh
./install_raspberry.sh
```

Or manual installation:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure the System

Edit `config.py` to match your setup:

```python
# Hardware mode: "RASPBERRY_PI" or "PC"
HARDWARE_MODE = "RASPBERRY_PI"

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# GPIO pins (Raspberry Pi only)
BUZZER_PIN = 18
ULTRASONIC_TRIG = 23
ULTRASONIC_ECHO = 24
LCD_I2C_ADDRESS = 0x27
```

### Step 4: Test Hardware

```bash
source venv/bin/activate
python test_hardware.py
```

### Step 5: Set Up Services (Auto-start)

```bash
# Copy service files
sudo cp attendance.service /etc/systemd/system/
sudo cp web_manager.service /etc/systemd/system/

# Enable services
sudo systemctl enable attendance.service
sudo systemctl enable web_manager.service

# Start services
sudo systemctl start attendance.service
sudo systemctl start web_manager.service
```

---

## 🗄️ Database Schema

The system uses SQLite with two main tables:

### Students Table

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    aruco_id INTEGER UNIQUE NOT NULL,
    face_embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| Column           | Type      | Description                               |
| ---------------- | --------- | ----------------------------------------- |
| `id`             | INTEGER   | Auto-incrementing primary key             |
| `name`           | TEXT      | Student's full name                       |
| `aruco_id`       | INTEGER   | Unique ArUco marker ID (0-249)            |
| `face_embedding` | BLOB      | Serialized face embedding vector (pickle) |
| `created_at`     | TIMESTAMP | Enrollment timestamp                      |

### Attendance Table

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, date)
);
```

| Column       | Type    | Description                   |
| ------------ | ------- | ----------------------------- |
| `id`         | INTEGER | Auto-incrementing primary key |
| `student_id` | INTEGER | Foreign key to students table |
| `date`       | TEXT    | Attendance date (YYYY-MM-DD)  |
| `time`       | TEXT    | Check-in time (HH:MM:SS)      |
| `status`     | TEXT    | Attendance status ("present") |

### Database Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│      STUDENTS       │       │     ATTENDANCE      │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │───┐   │ id (PK)             │
│ name                │   │   │ student_id (FK)  ◄──┘
│ aruco_id (UNIQUE)   │   │   │ date               │
│ face_embedding      │   │   │ time               │
│ created_at          │   │   │ status             │
└─────────────────────┘   │   │                     │
                          │   │ UNIQUE(student_id,  │
                          └──►│        date)        │
                              └─────────────────────┘
```

### Database Location

```
~/ai/data/attendance.db
```

### Viewing Database (Command Line)

```bash
sqlite3 ~/ai/data/attendance.db

# List all students
SELECT id, name, aruco_id, created_at FROM students;

# View today's attendance
SELECT s.name, a.time, a.status
FROM attendance a
JOIN students s ON a.student_id = s.id
WHERE a.date = date('now');

# Exit
.quit
```

---

## 🌐 Web UI Guide

### Accessing the Web UI

1. **Same WiFi Network**: `http://<raspberry-pi-ip>:4000`
2. **Hotspot Mode**: `http://10.42.0.1:4000`

Find Pi's IP: `hostname -I`

### Home Screen

![Home](https://via.placeholder.com/300x500?text=Home+Screen)

The home screen shows:

- **Students Enrolled**: Total number of registered students
- **Present Today**: Students who checked in today
- **Quick Actions**: Navigation buttons

### 📱 Navigation

| Button            | Function                        |
| ----------------- | ------------------------------- |
| 🏠 **Home**       | Dashboard with stats            |
| 👥 **Students**   | View/delete enrolled students   |
| ➕ **Enroll**     | Add new students                |
| ✅ **Attendance** | View today's attendance         |
| ⚙️ **Settings**   | System settings & hotspot guide |

---

### ➕ Enrolling a New Student

1. **Go to Enroll** page (tap ➕)

2. **Enter Student Details**:

   - Student Name
   - ArUco Marker ID (0-249)

3. **Tap "Start Enrollment"**

4. **Face Capture**:

   - Position student's face in front of camera
   - Wait for green checkmark

5. **ArUco Verification**:

   - Show the ArUco marker to camera
   - Wait for verification

6. **Complete**: Student is enrolled!

> **Note**: The system automatically stops the attendance service during enrollment to use the camera, then restarts it after.

---

### 👥 Managing Students

**View Students**:

- Shows all enrolled students with their ArUco IDs

**Delete Student**:

- Tap 🗑️ next to student name
- Confirm deletion

**Delete All Students**:

- Scroll down and tap "Delete All Students"
- ⚠️ This cannot be undone!

---

### ✅ Viewing Attendance

The attendance page shows:

- **Present Count**: X out of Y students
- **Attendance Rate**: Percentage
- **Attendance Log**: List of students with check-in times

---

### 🔄 Reset Attendance

Use to allow a student to check in again:

1. Go to **Reset** page
2. Find the student
3. Tap **Reset** button

**Reset All Today**: Clears all attendance for today

---

### 🖨️ Generate ArUco Markers

1. Go to **Enroll** page
2. Scroll to "Generate ArUco Markers"
3. Enter:
   - Start ID (default: 0)
   - Count (default: 30)
4. Tap **Generate Markers**
5. Find markers in: `~/ai/aruco_markers/`

Print the markers and assign one to each student.

---

## 📶 WiFi Hotspot Setup

Make your Raspberry Pi a WiFi hotspot for direct phone connection.

### Quick Setup (NetworkManager)

```bash
# Create hotspot
sudo nmcli device wifi hotspot ssid "AttendancePi" password "attendance123"

# Make it permanent (start on boot)
sudo nmcli connection modify Hotspot connection.autoconnect yes
```

### Connect from Phone

1. **WiFi**: AttendancePi
2. **Password**: attendance123
3. **Browser**: `http://10.42.0.1:4000`

### Disable Hotspot (Return to WiFi)

```bash
# Disable hotspot
sudo nmcli connection down Hotspot

# Connect to your WiFi
sudo nmcli device wifi connect "YourWiFi" password "YourPassword"
```

### Using the Setup Script

```bash
chmod +x setup_hotspot.sh
sudo bash setup_hotspot.sh
```

---

## 🚀 Running the System

### Manual Start

```bash
cd ~/ai
source venv/bin/activate

# Terminal 1: Start Attendance Engine
python main_attendance.py

# Terminal 2: Start Web Manager
python web_manager.py
```

### Service Commands

```bash
# Start services
sudo systemctl start attendance.service
sudo systemctl start web_manager.service

# Stop services
sudo systemctl stop attendance.service
sudo systemctl stop web_manager.service

# Restart services
sudo systemctl restart attendance.service
sudo systemctl restart web_manager.service

# View logs
sudo journalctl -u attendance.service -f
sudo journalctl -u web_manager.service -f
```

---

## 🔧 Troubleshooting

### Camera Issues

**Error**: "Camera **init** sequence did not complete"

```bash
# Stop attendance service
sudo systemctl stop attendance.service

# Test camera
rpicam-hello

# If camera works, restart service
sudo systemctl start attendance.service
```

### Web UI Not Loading

```bash
# Check if web manager is running
sudo systemctl status web_manager.service

# Check Pi's IP
hostname -I

# Try both IPs
http://<ip>:4000
http://10.42.0.1:4000
```

### Face Not Detected

- Ensure good lighting
- Face should be clearly visible
- Only one face in frame
- Remove glasses if reflective

### ArUco Not Detected

- Print marker clearly (no blur)
- Hold marker flat to camera
- Ensure good lighting
- Marker size: at least 5cm x 5cm

### Database Reset

```bash
# Backup first!
cp ~/ai/data/attendance.db ~/ai/data/attendance.db.backup

# Reset database
rm ~/ai/data/attendance.db
python -c "from database.db_manager import DatabaseManager; DatabaseManager('data/attendance.db')"
```

---

## 📁 Project Structure

```
attendance_system/
├── ai/
│   ├── aruco_detector.py    # ArUco marker detection
│   ├── face_detector.py     # Face detection
│   └── face_recognition.py  # Face embedding & matching
├── database/
│   └── db_manager.py        # SQLite database operations
├── hardware/
│   ├── camera.py            # Camera interface
│   ├── lcd.py               # LCD display control
│   ├── buzzer.py            # Buzzer control
│   └── ultrasonic.py        # Ultrasonic sensor
├── utils/
│   └── similarity.py        # Face similarity calculation
├── data/
│   └── attendance.db        # SQLite database
├── aruco_markers/           # Generated ArUco markers
├── config.py                # Configuration settings
├── main_attendance.py       # Main attendance engine
├── web_manager.py           # Flask web UI
├── enroll_students.py       # CLI enrollment script
├── attendance.service       # Systemd service file
├── web_manager.service      # Systemd service file
├── setup_hotspot.sh         # WiFi hotspot setup
└── requirements.txt         # Python dependencies
```

---

## 📄 License

This project is open source. Feel free to modify and use for your needs.

---

## 🆘 Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `sudo journalctl -u attendance.service -f`
3. Open an issue on GitHub

---

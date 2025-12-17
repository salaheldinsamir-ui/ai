# AI-Powered Attendance System

An automated attendance system using face recognition and ArUco tag verification, designed to run on both PC (development) and Raspberry Pi 4 (production).

## 🎯 Features

- **Dual Authentication**: Face recognition + ArUco marker verification
- **Presence Detection**: Ultrasonic sensors prevent spoofing attacks
- **One-Time Enrollment**: Secure enrollment with permanent attendance operation
- **Hardware Abstraction**: Seamless transition from PC to Raspberry Pi
- **Real-time Processing**: Continuous attendance monitoring
- **LCD Display & Buzzer**: Visual and audio feedback

## 📁 Project Structure

```
attendance_system/
├── main_attendance.py          # Main attendance program (auto-start)
├── enroll_students.py          # One-time student enrollment
├── attendance_engine.py        # Core attendance logic
├── config.py                   # System configuration
├── requirements.txt            # Python dependencies
│
├── ai/                         # AI modules
│   ├── face_detector.py       # Face detection
│   ├── face_recognition.py    # Face embedding & recognition
│   └── aruco_detector.py      # ArUco marker detection
│
├── hardware/                   # Hardware abstraction
│   ├── camera.py              # Camera interface (PC/Pi)
│   ├── ultrasonic.py          # Ultrasonic sensors
│   ├── lcd.py                 # LCD display
│   └── buzzer.py              # Buzzer control
│
├── database/                   # Database management
│   ├── db_manager.py          # SQLite operations
│   └── attendance.db          # SQLite database (created on first run)
│
└── utils/                      # Utilities
    └── similarity.py          # Cosine similarity calculation
```

## 🚀 Phase 1: PC Development & Testing

### Prerequisites

- Python 3.8 or higher
- Webcam
- Windows/Linux/MacOS

### Installation

1. **Clone or download this project**

2. **Install dependencies**:

```bash
cd attendance_system
pip install -r requirements.txt
```

3. **Configure for PC mode**:

   Open [config.py](config.py) and ensure:

   ```python
   HARDWARE_MODE = "PC"
   ```

### Usage

#### Step 1: Generate ArUco Markers

```bash
python enroll_students.py
# Select option 2: Generate ArUco markers
```

This creates printable ArUco markers in the `aruco_markers/` folder. Print these markers for each student.

#### Step 2: Enroll Students

```bash
python enroll_students.py
# Select option 1: Enroll students
```

For each student:

1. Enter their name
2. Position face in front of camera and press SPACE
3. Show ArUco marker to camera and press SPACE
4. Repeat for all students

#### Step 3: Run Attendance System

```bash
python main_attendance.py
```

The system will:

- Display camera feed in a window
- Continuously check for face + ArUco markers
- Mark attendance when all conditions are met
- Show status on terminal (simulating LCD)
- Play beep sounds (simulating buzzer)

**Controls**:

- `Q`: Quit
- `S`: Show attendance statistics

### Viewing Enrolled Students

```bash
python enroll_students.py
# Select option 3: View enrolled students
```

## 🔧 Phase 2: Raspberry Pi Deployment

### Hardware Requirements

- Raspberry Pi 4 (4GB)
- Pi Camera (5MP or higher)
- 2× Ultrasonic Sensors (HC-SR04)
- I2C LCD Display (16x2)
- Buzzer
- Jumper wires
- Power supply

### Wiring Diagram

**Ultrasonic Sensor 1**:

- Trigger: GPIO 23
- Echo: GPIO 24

**Ultrasonic Sensor 2**:

- Trigger: GPIO 27
- Echo: GPIO 22

**LCD Display**:

- I2C Address: 0x27 (default)
- SDA: GPIO 2
- SCL: GPIO 3

**Buzzer**:

- Signal: GPIO 17
- GND: Ground

### Raspberry Pi Setup

1. **Install Raspberry Pi OS** (64-bit recommended)

2. **Enable camera and I2C**:

```bash
sudo raspi-config
# Interface Options → Camera → Enable
# Interface Options → I2C → Enable
# Reboot
```

3. **Install dependencies**:

```bash
cd attendance_system
pip install -r requirements.txt

# Raspberry Pi specific
sudo apt-get install python3-picamera2
pip install RPi.GPIO RPLCD
```

4. **Configure for Raspberry Pi mode**:

   Edit [config.py](config.py):

   ```python
   HARDWARE_MODE = "RASPBERRY_PI"
   ```

5. **Copy enrolled database from PC**:

   Transfer `database/attendance.db` from PC to Raspberry Pi

6. **Run attendance system**:

```bash
python main_attendance.py
```

### Auto-Start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/attendance.service
```

Add:

```ini
[Unit]
Description=Attendance System
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/attendance_system
ExecStart=/usr/bin/python3 /home/pi/attendance_system/main_attendance.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable attendance.service
sudo systemctl start attendance.service
```

## ⚙️ Configuration

Edit [config.py](config.py) to customize:

- **Face Recognition**:

  - `FACE_RECOGNITION_THRESHOLD`: Similarity threshold (0.6 default)
  - `FACE_MODEL`: Model choice ("Facenet", "VGG-Face", "ArcFace")

- **Camera**:

  - `CAMERA_WIDTH`, `CAMERA_HEIGHT`: Resolution
  - `CAMERA_INDEX`: Webcam index (PC only)

- **Distance Detection**:

  - `MIN_DISTANCE`: Minimum valid distance (30 cm)
  - `MAX_DISTANCE`: Maximum valid distance (100 cm)

- **ArUco**:
  - `ARUCO_DICT`: Dictionary type ("DICT_4X4_50" default)

## 🔒 Security Features

1. **Dual Authentication**: Requires both face match AND ArUco tag match
2. **Single Person Validation**: Rejects multiple faces in frame
3. **Anti-Spoofing**: Ultrasonic sensors validate physical presence
4. **Quality Checks**: Validates image brightness, contrast, and sharpness
5. **One-Time Enrollment**: No runtime face registration possible
6. **Daily Attendance**: Prevents duplicate attendance on same day

## 📊 Database Schema

**students table**:

```sql
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL
aruco_id        INTEGER UNIQUE NOT NULL
face_embedding  BLOB NOT NULL
created_at      TIMESTAMP
```

**attendance table**:

```sql
id          INTEGER PRIMARY KEY
student_id  INTEGER (foreign key)
date        TEXT (YYYY-MM-DD)
time        TEXT (HH:MM:SS)
status      TEXT (default: "Present")
UNIQUE(student_id, date)  -- Prevents duplicates
```

## 🐛 Troubleshooting

### PC Mode Issues

**Camera not detected**:

- Check camera permissions
- Try different `CAMERA_INDEX` values (0, 1, 2)

**Face recognition slow**:

- Reduce camera resolution in [config.py](config.py)
- Use lighter model like "OpenFace"

**DeepFace installation issues**:

```bash
pip install --upgrade deepface tf-keras tensorflow
```

### Raspberry Pi Issues

**Camera not working**:

```bash
# Check camera detection
libcamera-hello

# If using old Pi Camera v1
sudo raspi-config  # Enable legacy camera
```

**I2C LCD not detected**:

```bash
# Scan I2C devices
sudo i2cdetect -y 1

# If address differs from 0x27, update config.py
```

**GPIO permission denied**:

```bash
sudo usermod -a -G gpio pi
sudo reboot
```

## 📈 Performance

**PC Mode**:

- Face detection: ~30 FPS
- Face recognition: ~2-3 seconds per check
- Memory usage: ~500 MB

**Raspberry Pi 4**:

- Face detection: ~15 FPS
- Face recognition: ~3-5 seconds per check
- Memory usage: ~1 GB

## 🔄 Updating from PC to Pi

1. Test thoroughly on PC
2. Copy entire project folder to Raspberry Pi
3. Transfer `database/attendance.db`
4. Change `HARDWARE_MODE` to "RASPBERRY_PI"
5. Install Pi-specific libraries
6. No code changes needed!

## 📝 License

This project is provided as-is for educational purposes.

## 👥 Contributing

Improvements welcome! Focus areas:

- Multi-threading for performance
- Additional anti-spoofing methods
- Web interface for attendance reports
- Email notifications

## 📧 Support

For issues, check:

1. Configuration in [config.py](config.py)
2. Log output in terminal
3. Database integrity
4. Camera and hardware connections

---

**System Status**: ✓ PC Development Ready | ⏳ Raspberry Pi Deployment Ready

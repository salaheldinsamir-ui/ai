# Raspberry Pi 4 Circuit Wiring Guide

## AI-Powered Attendance System

---

## 📋 Required Components

### Main Components

- **Raspberry Pi 4 Model B (4GB RAM)**
- **Raspberry Pi Camera Module V2** or USB Webcam
- **16x2 I2C LCD Display** (PCF8574 backpack)
- **2x HC-SR04 Ultrasonic Sensors**
- **Active Buzzer Module** (5V)
- **Power Supply**: 5V 3A USB-C for Raspberry Pi
- **microSD Card**: 32GB or larger with Raspberry Pi OS

### Additional Components

- **Breadboard** (830 points recommended)
- **Jumper Wires** (Male-to-Female and Male-to-Male)
- **Resistors**:
  - 2x 1kΩ (for ultrasonic echo pins)
  - 2x 2kΩ (for ultrasonic echo pins - voltage divider)
- **Power Strip** or **5V Breadboard Power Supply**

---

## 🔌 Pin Configuration Summary

### Raspberry Pi 4 GPIO Pinout Used

| Component                  | Pin Type      | GPIO Pin     | Physical Pin                      | Notes                |
| -------------------------- | ------------- | ------------ | --------------------------------- | -------------------- |
| **Camera**                 | CSI Connector | -            | CSI Port                          | Use ribbon cable     |
| **Ultrasonic 1 - Trigger** | Output        | GPIO 23      | Pin 16                            | 3.3V logic           |
| **Ultrasonic 1 - Echo**    | Input         | GPIO 24      | Pin 18                            | Via voltage divider! |
| **Ultrasonic 2 - Trigger** | Output        | GPIO 27      | Pin 13                            | 3.3V logic           |
| **Ultrasonic 2 - Echo**    | Input         | GPIO 22      | Pin 15                            | Via voltage divider! |
| **LCD - SDA**              | I2C Data      | GPIO 2 (SDA) | Pin 3                             | I2C Bus              |
| **LCD - SCL**              | I2C Clock     | GPIO 3 (SCL) | Pin 5                             | I2C Bus              |
| **Buzzer**                 | Output        | GPIO 17      | Pin 11                            | 3.3V/5V compatible   |
| **Ground**                 | GND           | Ground       | Pins 6, 9, 14, 20, 25, 30, 34, 39 | Multiple GND needed  |
| **5V Power**               | 5V            | +5V          | Pins 2, 4                         | For LCD & Sensors    |

---

## 🔧 Detailed Component Wiring

### 1️⃣ **Raspberry Pi Camera Module**

**Connection:**

```
Pi Camera V2 → Raspberry Pi 4 CSI Port
├─ Use the 15-pin ribbon cable (included with camera)
├─ Lift the CSI port lock (between HDMI ports)
├─ Insert ribbon with blue side facing Ethernet port
└─ Press lock down firmly
```

**Configuration in Code:**

```python
# config.py
HARDWARE_MODE = "RASPBERRY_PI"
CAMERA_INDEX = 0  # For Pi Camera
```

**Enable Camera:**

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

---

### 2️⃣ **Ultrasonic Sensor 1 (HC-SR04)**

**⚠️ CRITICAL: HC-SR04 outputs 5V on ECHO pin, but Raspberry Pi GPIO pins are 3.3V tolerant!**
**You MUST use a voltage divider to protect the Pi!**

**Wiring with Voltage Divider:**

```
HC-SR04 Sensor 1:
├─ VCC  → 5V Power (Pin 2 or Pin 4)
├─ GND  → Ground (Pin 6)
├─ TRIG → GPIO 23 (Pin 16) [Direct connection - OK, it's an output]
└─ ECHO → Voltage Divider → GPIO 24 (Pin 18)

Voltage Divider for ECHO pin:
HC-SR04 ECHO Pin
    │
    ├── 1kΩ Resistor ──┬── GPIO 24 (Pin 18)
    │                  │
    └── 2kΩ Resistor ──┴── Ground

This creates 5V × (2kΩ/(1kΩ+2kΩ)) = 3.3V safe voltage!
```

**Configuration in Code:**

```python
# config.py
ULTRASONIC_SENSOR_1_TRIGGER = 23  # GPIO 23 (Physical Pin 16)
ULTRASONIC_SENSOR_1_ECHO = 24     # GPIO 24 (Physical Pin 18)
```

---

### 3️⃣ **Ultrasonic Sensor 2 (HC-SR04)**

**Same voltage divider setup!**

**Wiring:**

```
HC-SR04 Sensor 2:
├─ VCC  → 5V Power (Pin 4)
├─ GND  → Ground (Pin 9)
├─ TRIG → GPIO 27 (Pin 13) [Direct connection]
└─ ECHO → Voltage Divider → GPIO 22 (Pin 15)

Voltage Divider for ECHO pin:
HC-SR04 ECHO Pin
    │
    ├── 1kΩ Resistor ──┬── GPIO 22 (Pin 15)
    │                  │
    └── 2kΩ Resistor ──┴── Ground
```

**Configuration in Code:**

```python
# config.py
ULTRASONIC_SENSOR_2_TRIGGER = 27  # GPIO 27 (Physical Pin 13)
ULTRASONIC_SENSOR_2_ECHO = 22     # GPIO 22 (Physical Pin 15)
```

**Sensor Placement:**

- Mount 45cm from expected standing position
- Both sensors facing same direction
- Height: Eye level (150-170cm)

---

### 4️⃣ **16x2 I2C LCD Display**

**Wiring:**

```
LCD Module (with I2C backpack):
├─ VCC → 5V Power (Pin 2)
├─ GND → Ground (Pin 14)
├─ SDA → GPIO 2/SDA (Pin 3)
└─ SCL → GPIO 3/SCL (Pin 5)
```

**Configuration in Code:**

```python
# config.py
LCD_I2C_ADDRESS = 0x27  # Default address, may be 0x3F
LCD_ROWS = 2
LCD_COLS = 16
```

**Find I2C Address:**

```bash
sudo apt-get install i2c-tools
sudo i2cdetect -y 1
# Look for address (usually 0x27 or 0x3F)
```

**Enable I2C:**

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

**Install I2C Library:**

```bash
sudo pip3 install RPLCD
```

---

### 5️⃣ **Active Buzzer Module**

**Wiring:**

```
Buzzer Module:
├─ VCC/+ → GPIO 17 (Pin 11) [Can also use 5V if module needs it]
├─ GND/- → Ground (Pin 25)
└─ Signal → GPIO 17 (Pin 11) [For 3-pin modules]

Note: Active buzzer = built-in oscillator, just needs DC power
```

**Configuration in Code:**

```python
# config.py
BUZZER_PIN = 17  # GPIO 17 (Physical Pin 11)
```

**Buzzer Types:**

- **Active Buzzer**: Recommended (simpler, used in code)
- **Passive Buzzer**: Needs PWM signal (more complex)

---

## 🎨 Complete Circuit Diagram (Text-based)

```
Raspberry Pi 4 GPIO Layout (Top View):
┌─────────────────────────────────────┐
│                                     │
│  3V3  (1) ● ● (2)  5V ◄───── LCD VCC, Sensors VCC
│  SDA  (3) ● ● (4)  5V      ▲
│  SCL  (5) ● ● (6)  GND     │ I2C to LCD
│   -   (7) ● ● (8)   -      │
│  GND  (9) ● ● (10)  -      │
│ GP17 (11) ● ● (12)  -      │ Buzzer Signal
│ GP27 (13) ● ● (14) GND ◄───┼─── LCD GND, Sensors GND
│ GP22 (15) ● ● (16) GP23    │ Ultrasonic 2 Echo / Trigger
│  3V3 (17) ● ● (18) GP24    │ Ultrasonic 1 Echo
│   -  (19) ● ● (20) GND     │
│   -  (21) ● ● (22)  -      │
│   -  (23) ● ● (24)  -      │
│  GND (25) ● ● (26)  -      │ Buzzer GND
│   -  (27) ● ● (28)  -      │
│   -  (29) ● ● (30) GND     │
│   -  (31) ● ● (32)  -      │
│   -  (33) ● ● (34) GND     │
│   -  (35) ● ● (36)  -      │
│   -  (37) ● ● (38)  -      │
│  GND (39) ● ● (40)  -      │
└─────────────────────────────────────┘
```

---

## 🔨 Assembly Steps

### Step 1: Prepare the Breadboard

1. Place breadboard on stable surface
2. Connect **5V rail** from Pi Pin 2 → Breadboard + rail
3. Connect **GND rail** from Pi Pin 6 → Breadboard - rail

### Step 2: Build Voltage Dividers (Critical!)

**For Ultrasonic Sensor 1 Echo:**

1. Place 1kΩ resistor: ECHO pin → Row A
2. Place 2kΩ resistor: Row A → GND rail
3. Connect Row A → GPIO 24 (Pin 18)

**For Ultrasonic Sensor 2 Echo:**

1. Place 1kΩ resistor: ECHO pin → Row B
2. Place 2kΩ resistor: Row B → GND rail
3. Connect Row B → GPIO 22 (Pin 15)

### Step 3: Connect Ultrasonic Sensors

**Sensor 1:**

- VCC → 5V rail
- GND → GND rail
- TRIG → GPIO 23 (Pin 16)
- ECHO → Voltage divider Row A

**Sensor 2:**

- VCC → 5V rail
- GND → GND rail
- TRIG → GPIO 27 (Pin 13)
- ECHO → Voltage divider Row B

### Step 4: Connect LCD Display

- VCC → 5V rail (or direct to Pin 2)
- GND → GND rail (or direct to Pin 14)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

### Step 5: Connect Buzzer

- VCC/+ → GPIO 17 (Pin 11)
- GND/- → GND rail (or direct to Pin 25)

### Step 6: Connect Camera

- Carefully insert ribbon cable into CSI port
- Blue side facing Ethernet port
- Lock firmly

---

## 🧪 Testing Individual Components

### Test Ultrasonic Sensors:

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
time.sleep(0.1)

GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)

while GPIO.input(ECHO) == 0:
    pulse_start = time.time()

while GPIO.input(ECHO) == 1:
    pulse_end = time.time()

distance = (pulse_end - pulse_start) * 17150
print(f"Distance: {distance:.1f} cm")

GPIO.cleanup()
```

### Test LCD:

```python
from RPLCD.i2c import CharLCD

lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
lcd.write_string('Hello World!')
```

### Test Buzzer:

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

GPIO.output(17, True)  # Buzzer ON
time.sleep(1)
GPIO.output(17, False)  # Buzzer OFF

GPIO.cleanup()
```

### Test Camera:

```bash
libcamera-hello --timeout 5000
# Or for legacy:
raspistill -o test.jpg
```

---

## ⚙️ Software Configuration

### 1. Update config.py:

```python
HARDWARE_MODE = "RASPBERRY_PI"
```

### 2. Install Dependencies:

```bash
cd /home/pi/attendance_system
sudo pip3 install -r requirements.txt
sudo pip3 install RPLCD RPi.GPIO
```

### 3. Enable Interfaces:

```bash
sudo raspi-config
# Enable: Camera, I2C, SSH (optional)
sudo reboot
```

### 4. Set Permissions:

```bash
sudo usermod -a -G i2c,gpio,video pi
```

### 5. Run System:

```bash
cd /home/pi/attendance_system
python3 main_attendance.py
```

---

## 🚨 Troubleshooting

### Ultrasonic Sensor Not Working

- **Check voltage divider** - Most common issue!
- Verify resistor values with multimeter
- Test voltage at GPIO pin (should be ~3.3V max)
- Check connections are firm

### LCD Not Displaying

- Run `sudo i2cdetect -y 1` to find address
- Try address 0x3F if 0x27 doesn't work
- Check SDA/SCL aren't swapped
- Verify 5V power connected

### Camera Not Detected

```bash
vcgencmd get_camera
# Should show: supported=1 detected=1
```

- Check ribbon cable orientation
- Ensure camera enabled in raspi-config

### Buzzer Silent

- Test with multimeter - should show voltage when active
- Try connecting VCC to 5V instead of GPIO 17
- Verify it's an active buzzer (has oscillator)

### GPIO Permission Denied

```bash
sudo chmod a+rw /dev/gpiomem
sudo usermod -a -G gpio pi
```

---

## 🔋 Power Considerations

**Total Current Draw:**

- Raspberry Pi 4: ~600mA (idle), ~1.2A (peak)
- Pi Camera: ~250mA
- LCD Backlight: ~100mA
- Ultrasonic Sensors: 2 × 15mA = 30mA
- Buzzer: ~30mA

**Total: ~2A peak**

**Recommended Power Supply: 5V 3A USB-C**

---

## 📸 Mounting Recommendations

### Camera Position:

- Height: 150-170cm (face level)
- Distance: 60-100cm from standing position
- Angle: Slight downward tilt (5-10°)

### Ultrasonic Sensors:

- Mount at 45cm from expected position
- Both sensors parallel, facing forward
- Avoid metal surfaces nearby (causes reflections)

### LCD Display:

- Eye level, visible angle
- Avoid direct sunlight (hard to read)

---

## ✅ Final Checklist

- [ ] All components connected with correct polarity
- [ ] Voltage dividers in place for ultrasonic ECHO pins
- [ ] I2C address confirmed for LCD
- [ ] Camera ribbon cable properly seated
- [ ] All ground connections secure
- [ ] 5V power rail connected
- [ ] GPIO pins match config.py
- [ ] Test each component individually
- [ ] Run full system test
- [ ] Configure auto-start (optional)

---

## 🔄 Auto-Start on Boot (Optional)

Create service file:

```bash
sudo nano /etc/systemd/system/attendance.service
```

Add:

```ini
[Unit]
Description=AI Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/attendance_system
ExecStart=/usr/bin/python3 /home/pi/attendance_system/main_attendance.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable attendance.service
sudo systemctl start attendance.service
```

---

## 📞 Support

If you encounter issues:

1. Check all connections match this guide
2. Test each component individually
3. Verify GPIO pin numbers in config.py
4. Check system logs: `journalctl -u attendance.service`

---

**🎉 Your attendance system is now ready to deploy!**

# COMPLETE Raspberry Pi Setup Guide - From Zero to Running

## AI-Powered Attendance System - Full Step-by-Step Guide

---

## 📋 WHAT YOU NEED

### Physical Items:

- ✅ Raspberry Pi 4 Model B (4GB)
- ✅ microSD Card (32GB+, Class 10)
- ✅ USB-C Power Supply (5V 3A)
- ✅ microSD Card Reader (USB adapter)
- ✅ Your Windows PC
- ✅ Ethernet cable (optional but recommended)
- ✅ For SSH setup: Just the items above
- ✅ For direct setup: Monitor, micro HDMI cable, keyboard, mouse

### Downloads Needed:

- Raspberry Pi Imager (we'll download this)

---

## 🎯 OVERVIEW: What We're Going to Do

```
STEP 1: Flash SD Card with OS
         ↓
STEP 2: Add Your Project Files to SD Card (YES, WE CAN DO THIS!)
         ↓
STEP 3: Put SD Card in Raspberry Pi & Boot
         ↓
STEP 4: Connect via SSH (or direct if you have monitor)
         ↓
STEP 5: Install Dependencies
         ↓
STEP 6: Configure & Run Your Attendance System
         ↓
STEP 7: Set Up Auto-Start
         ↓
DONE! System Running 24/7
```

---

# PART 1: FLASH THE SD CARD (On Your Windows PC)

## Step 1.1: Download Raspberry Pi Imager

1. **Open your browser**
2. **Go to**: https://www.raspberrypi.com/software/
3. **Click**: "Download for Windows"
4. **File downloads**: `imager_1.x.x.exe` (about 20MB)
5. **Find file** in Downloads folder
6. **Double-click** to install
7. **Click "Yes"** when Windows asks for permission
8. **Follow installer** → Click "Install" → Click "Finish"

---

## Step 1.2: Prepare Your microSD Card

1. **Take microSD card** out of package
2. **Insert into microSD card reader** (the USB adapter)
3. **Plug card reader** into your PC's USB port
4. **Windows detects it** - you might hear a sound
5. **Close any windows** that pop up asking to format

⚠️ **WARNING**: Next step will ERASE everything on this card!

---

## Step 1.3: Flash Raspberry Pi OS onto SD Card

1. **Open "Raspberry Pi Imager"** (on desktop or Start menu)

2. **Main screen appears**:

   ```
   ┌────────────────────────────────┐
   │  Raspberry Pi Imager           │
   ├────────────────────────────────┤
   │  [CHOOSE DEVICE]               │
   │  [CHOOSE OS]                   │
   │  [CHOOSE STORAGE]              │
   │            [NEXT]              │
   └────────────────────────────────┘
   ```

3. **Click "CHOOSE DEVICE"**:

   - Select: **Raspberry Pi 4**
   - Click it

4. **Click "CHOOSE OS"**:

   - Select: **Raspberry Pi OS (64-bit)**
   - Should say "Recommended" and "Debian Bookworm with desktop"
   - ⚠️ **NOT** "Lite" version - we want the full version
   - Click it

5. **Click "CHOOSE STORAGE"**:

   - You'll see your microSD card listed (shows size like "32 GB")
   - ⚠️ **MAKE SURE** it's the SD card, not your PC hard drive!
   - Click it

6. **Click "NEXT"**

7. **Important popup appears**:
   ```
   "Would you like to apply OS customisation settings?"
   ```
   - **Click "EDIT SETTINGS"** (NOT "NO")

---

## Step 1.4: Configure OS Settings (CRITICAL!)

This is where you set up WiFi, SSH, and password!

### GENERAL Tab:

```
✅ Set hostname: attendance-pi
   (This is your Raspberry Pi's name on network)

✅ Set username and password:
   Username: pi
   Password: [Type a strong password]

   📝 WRITE DOWN YOUR PASSWORD! You'll need it!

✅ Configure wireless LAN:
   SSID: [Your WiFi network name]
   Password: [Your WiFi password]
   Wireless LAN country: [Your country, e.g., US, GB, EG]

   ⚠️ IMPORTANT:
   - Type WiFi name EXACTLY (case-sensitive!)
   - Raspberry Pi 4 only works with 2.4GHz WiFi (not 5GHz)
   - Make sure your router has 2.4GHz enabled

✅ Set locale settings:
   Time zone: [Your timezone, e.g., Africa/Cairo, America/New_York]
   Keyboard layout: us
```

### SERVICES Tab:

```
✅ Enable SSH
   ● Use password authentication

   ⚠️ THIS IS CRITICAL FOR REMOTE ACCESS!
   Check this box even if you plan to use monitor!
```

### OPTIONS Tab:

```
✅ Enable telemetry: [Uncheck if you want privacy]
□ Eject media when finished: [Check this]
```

**Click "SAVE"**

---

## Step 1.5: Start Flashing

1. **Confirmation popup**:

   ```
   "All existing data on 'YOUR_SD_CARD' will be erased.
    Are you sure you want to continue?"
   ```

   - Double-check it's the right card
   - **Click "YES"**

2. **Flashing starts!**

   ```
   ┌─────────────────────────────────┐
   │ Writing...                      │
   │ [████████████░░░░░░░] 65%       │
   │                                 │
   │ This may take several minutes   │
   └─────────────────────────────────┘
   ```

   **What's happening:**

   - Downloading Raspberry Pi OS (if first time) - 2-5 min
   - Writing to SD card - 5-10 min
   - Verifying (checking it wrote correctly) - 2-5 min

   **Total time: 10-20 minutes**

   ☕ Get coffee, this takes a while!

3. **Verification completes**:

   ```
   Verifying... [████████████████] 100%
   ```

4. **Success!**

   ```
   ┌─────────────────────────────────┐
   │ Write Successful                │
   │                                 │
   │ Raspberry Pi OS has been        │
   │ written to your SD card         │
   │                                 │
   │         [CONTINUE]              │
   └─────────────────────────────────┘
   ```

   - **Click "CONTINUE"**

5. **Windows might show errors** like:
   ```
   "You need to format the disk in drive E: before you can use it"
   ```
   - **IGNORE THESE!** Click "Cancel"
   - This is normal - Windows can't read Linux partitions

---

## Step 1.6: Add Your Project Files to SD Card

**IMPORTANT: DO THIS BEFORE EJECTING THE SD CARD!**

After flashing, the SD card has TWO partitions:

- **boot** partition (Windows can see this - labeled "bootfs")
- **rootfs** partition (Windows can't see this - Linux filesystem)

We'll add project files to the boot partition, then move them later.

### Method 1: Using Boot Partition (Easier)

1. **The SD card should still be in your PC**
2. **Open File Explorer**
3. **Look for drive labeled "bootfs"** or "boot" (usually D: or E:)
4. **Open this drive**
5. **Create new folder** named `attendance_project`
6. **Copy your project**:

   - Navigate to `E:\AI\attendance_system`
   - Select ALL files and folders:
     - config.py
     - main_attendance.py
     - attendance_engine.py
     - enroll_students.py
     - database/
     - hardware/
     - ai_modules/
     - requirements.txt
     - ALL other files
   - **Right-click** → **Copy**
   - Go back to boot drive → Open `attendance_project` folder
   - **Right-click** → **Paste**
   - **Wait for copy** (1-2 minutes)

7. **Verify files copied**:
   - You should see all your Python files in `bootfs:\attendance_project\`

---

## Step 1.7: Safely Eject SD Card

1. **In File Explorer**, right-click the "bootfs" drive
2. **Click "Eject"**
3. **Wait for "Safe to Remove Hardware"** message
4. **Remove card reader** from PC
5. **Remove microSD card** from card reader

**🎉 Your SD card is ready! It has:**

- ✅ Raspberry Pi OS installed
- ✅ WiFi configured
- ✅ SSH enabled
- ✅ Your project files copied

---

# PART 2: BOOT RASPBERRY PI

## Step 2.1: Insert SD Card into Raspberry Pi

1. **Find the microSD card slot**:

   - It's on the **BOTTOM** of the Raspberry Pi board
   - On the opposite side from the USB ports

2. **Orient the card correctly**:

   - Metal contacts facing **UP** (toward the board)
   - Label side facing **DOWN**

3. **Push gently** until it clicks

```
SIDE VIEW:
            ┌─────────────┐
            │  Pi Board   │
            └─────────────┘
microSD →  ═══╗         ║
              ╚═════════╝
    Push in this direction →
```

---

## Step 2.2: Connect Everything

**Do these in ORDER:**

1. ✅ **microSD card inserted** (done above)

2. **Optional but RECOMMENDED**: Connect Ethernet cable

   - From your router to Raspberry Pi Ethernet port
   - Makes finding IP address easier

3. **Connect USB-C Power** (DO THIS LAST!)
   - Plug USB-C cable into Raspberry Pi
   - Plug other end into wall outlet
   - **Pi starts immediately when power connected!**

**What you'll see:**

- 🔴 **Red LED** lights up solid = Power is good
- 🟢 **Green LED** blinks = SD card is being read, system is booting

---

## Step 2.3: Wait for Boot (2-3 minutes)

**First boot takes longer!**

What's happening:

1. Raspberry Pi reads OS from SD card (30 sec)
2. Applies your custom settings (WiFi, hostname, SSH) (1 min)
3. Connects to WiFi network (30 sec)
4. Ready for SSH connection!

**How to know it's ready:**

- Green LED stops blinking constantly
- Wait 3 full minutes to be safe

---

# PART 3: CONNECT TO RASPBERRY PI

You have TWO options: SSH (no monitor) or Direct (with monitor)

---

## OPTION A: Connect via SSH (No Monitor Needed)

### Step 3.1: Find Raspberry Pi's IP Address

**Method 1: Try the Hostname (Easiest)**

1. **Open PowerShell** on your PC (Windows key → type "PowerShell")
2. **Type**:
   ```powershell
   ping attendance-pi.local
   ```
3. **If it works, you'll see**:

   ```
   Pinging attendance-pi.local [192.168.1.150] with 32 bytes of data:
   Reply from 192.168.1.150: bytes=32 time=2ms TTL=64
   ```

   📝 **Write down that IP address!** (192.168.1.150 in this example)

4. **If it doesn't work**, try Method 2 below

---

**Method 2: Check Your Router**

1. **Open browser**
2. **Go to your router admin page**:
   - Usually: `192.168.1.1` or `192.168.0.1` or `192.168.100.1`
   - Check sticker on your router for the address
3. **Login**:
   - Common defaults: admin/admin or admin/password
   - Or check router sticker
4. **Find "Connected Devices"** or "DHCP Clients" or "Device List"
5. **Look for**:
   - Device name: `attendance-pi`
   - Or hostname: `attendance-pi`
6. 📝 **Write down the IP address** next to it

---

**Method 3: Use Network Scanner**

1. **Download "Advanced IP Scanner"**:
   - https://www.advanced-ip-scanner.com/
   - Free for Windows
2. **Install and run it**
3. **Click "Scan"**
4. **Look for**:
   - Manufacturer: "Raspberry Pi Foundation"
   - Name: "attendance-pi"
5. 📝 **Write down the IP address**

---

### Step 3.2: Connect via SSH

1. **Open PowerShell** (Windows key → type "PowerShell")

2. **Type** (replace with YOUR IP):

   ```powershell
   ssh pi@192.168.1.150
   ```

   Or if ping worked:

   ```powershell
   ssh pi@attendance-pi.local
   ```

3. **First time warning**:

   ```
   The authenticity of host '192.168.1.150' can't be established.
   Are you sure you want to continue connecting (yes/no)?
   ```

   - Type: `yes`
   - Press Enter

4. **Enter password**:

   ```
   pi@192.168.1.150's password:
   ```

   - Type the password you set in Raspberry Pi Imager
   - ⚠️ **You won't see anything as you type** (security feature)
   - Press Enter

5. **SUCCESS!** You'll see:

   ```
   Linux attendance-pi 6.1.0-rpi7-rpi-v8 ...

   pi@attendance-pi:~ $
   ```

**🎉 You're connected! Skip to PART 4.**

---

## OPTION B: Connect Directly (With Monitor)

### Step 3.1: Connect Hardware

1. **Connect micro HDMI cable**:

   - Micro HDMI end → Raspberry Pi **HDMI0** port (closer to USB-C)
   - Regular HDMI end → Your monitor

2. **Connect USB keyboard** to any USB port

3. **Connect USB mouse** to any USB port

4. **Turn on monitor** and select correct HDMI input

### Step 3.2: Wait for Desktop

After 2-3 minutes, you'll see:

- Rainbow square (2 sec)
- Text scrolling (boot messages)
- Raspberry Pi logo with progress bar
- **Desktop appears!**

### Step 3.3: Login (if asked)

- Username: `pi`
- Password: (what you set in Imager)

### Step 3.4: Open Terminal

1. **Click the black icon** at top of screen (looks like **>\_**)
2. **Terminal opens**:
   ```
   pi@attendance-pi:~ $
   ```

**You're ready! Continue to PART 4.**

---

# PART 4: MOVE PROJECT FILES & SETUP

## Step 4.1: Move Project Files from Boot Partition

**In Terminal (or SSH), type:**

```bash
ls /boot/firmware/attendance_project
```

**You should see your project files!**

**Move them to your home directory:**

```bash
mkdir -p /home/pi/attendance_system
sudo cp -r /boot/firmware/attendance_project/* /home/pi/attendance_system/
sudo chown -R pi:pi /home/pi/attendance_system
```

**Verify:**

```bash
ls /home/pi/attendance_system
```

**You should see:**

```
config.py
main_attendance.py
attendance_engine.py
enroll_students.py
database/
hardware/
ai_modules/
requirements.txt
...
```

✅ **Files are now in the right place!**

---

## Step 4.2: Update System (Takes 20-40 minutes)

**Type these commands (press Enter after each):**

```bash
sudo apt update
```

Wait for package list to update...

```bash
sudo apt upgrade -y
```

⏳ **This takes 20-40 minutes!** ☕ Be patient!

**When done, reboot:**

```bash
sudo reboot
```

**Wait 2 minutes**, then:

- **If using SSH**: Reconnect with `ssh pi@YOUR_IP`
- **If using monitor**: Desktop will appear again

---

## Step 4.3: Enable Required Interfaces

```bash
sudo raspi-config
```

**Navigate with arrow keys, Enter to select:**

1. **Select**: `3 Interface Options`
2. **Select**: `I1 Legacy Camera` → Select `Yes`
3. **Back to menu**, select: `3 Interface Options`
4. **Select**: `I5 I2C` → Select `Yes`
5. **Tab to "Finish"**, press Enter
6. **Select "Yes"** to reboot

**Wait 2 minutes, reconnect if using SSH**

---

## Step 4.4: Install System Dependencies

**Type each command, wait for completion:**

```bash
sudo apt install python3-pip python3-dev python3-venv -y
```

```bash
sudo apt install -y libopencv-dev python3-opencv libatlas-base-dev libjasper-dev libqtgui4 libqt4-test libhdf5-dev libhdf5-serial-dev
```

```bash
sudo apt install -y i2c-tools
```

```bash
sudo apt install -y python3-picamera2
```

```bash
sudo apt install -y python3-rpi.gpio python3-gpiozero
```

✅ **All system dependencies installed!**

---

# PART 5: INSTALL PYTHON DEPENDENCIES

## Step 5.1: Navigate to Project

```bash
cd /home/pi/attendance_system
```

## Step 5.2: Install Python Packages

**This takes 20-40 minutes!**

```bash
pip install -r requirements.txt
```

**You'll see:**

```
Collecting opencv-python
Collecting deepface
Collecting tensorflow
...
Installing collected packages: ...
```

⏳ **Wait patiently!** TensorFlow takes longest to install.

**If you get TensorFlow errors:**

```bash
pip install tensorflow-aarch64
```

✅ **All Python packages installed!**

---

# PART 6: CONFIGURE FOR RASPBERRY PI

## Step 6.1: Edit Configuration

```bash
nano /home/pi/attendance_system/config.py
```

**Find this line:**

```python
HARDWARE_MODE = "PC"
```

**Change to:**

```python
HARDWARE_MODE = "RASPBERRY_PI"
```

**Save and exit:**

- Press `Ctrl+O` (letter O)
- Press `Enter`
- Press `Ctrl+X`

---

## Step 6.2: Check GPIO Pin Configuration

```bash
nano /home/pi/attendance_system/config.py
```

**Verify these settings match your wiring:**

```python
# GPIO Pin Configuration
ULTRASONIC_SENSOR_1_TRIGGER = 23
ULTRASONIC_SENSOR_1_ECHO = 24
ULTRASONIC_SENSOR_2_TRIGGER = 27
ULTRASONIC_SENSOR_2_ECHO = 22
BUZZER_PIN = 17
LCD_I2C_ADDRESS = 0x27  # Or 0x3F - check with: sudo i2cdetect -y 1
```

**If you need to change LCD address:**

```bash
sudo i2cdetect -y 1
```

You'll see a number (27 or 3F) - update `LCD_I2C_ADDRESS` if different.

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

# PART 7: HARDWARE WIRING

**⚠️ BEFORE TESTING: Wire your hardware according to CIRCUIT_GUIDE.md!**

You need to connect:

- ✅ 2x HC-SR04 Ultrasonic Sensors (with voltage dividers!)
- ✅ 16x2 I2C LCD Display
- ✅ Active Buzzer
- ✅ Pi Camera Module

**See [CIRCUIT_GUIDE.md](CIRCUIT_GUIDE.md) for complete wiring instructions!**

---

# PART 8: TEST THE SYSTEM

## Step 8.1: First Test Run

```bash
cd /home/pi/attendance_system
python3 main_attendance.py
```

**You should see:**

```
==================================================
AI-POWERED ATTENDANCE SYSTEM
==================================================
Hardware Mode: RASPBERRY_PI
Starting at: 2025-12-16 15:30:00
==================================================

[Init] Initializing hardware components...
[Camera] Raspberry Pi camera initialized
[Ultrasonic] Raspberry Pi GPIO mode initialized
[LCD] Raspberry Pi LCD initialized (Address: 0x27)
[Buzzer] Raspberry Pi GPIO buzzer initialized

[Init] Initializing AI modules...
[Init] Connecting to database...
[Init] Database loaded: 3 students enrolled

ATTENDANCE SYSTEM ACTIVE
Press 'Ctrl+C' to quit
==================================================
```

## Step 8.2: Test Workflow

1. **Approach within 45cm** of sensors
2. **Hold face steady** for 2.5 seconds
3. **Face recognition** happens
4. **Show ArUco marker** to camera
5. **Attendance marked!**
6. **LCD shows**: "Attendance Taken!"
7. **Buzzer beeps** success tone

**To stop:**

- Press `Ctrl+C`

---

# PART 9: SET UP AUTO-START ON BOOT

## Step 9.1: Create Systemd Service

```bash
sudo nano /etc/systemd/system/attendance.service
```

**Paste this:**

```ini
[Unit]
Description=AI-Powered Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/attendance_system
ExecStart=/usr/bin/python3 /home/pi/attendance_system/main_attendance.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 9.2: Enable and Start Service

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable attendance.service
```

```bash
sudo systemctl start attendance.service
```

**Check status:**

```bash
sudo systemctl status attendance.service
```

**Should show:**

```
● attendance.service - AI-Powered Attendance System
   Loaded: loaded
   Active: active (running) since ...
```

**View live logs:**

```bash
sudo journalctl -u attendance.service -f
```

Press `Ctrl+C` to stop viewing logs.

---

# PART 10: USEFUL COMMANDS

## Service Management

**Start service:**

```bash
sudo systemctl start attendance.service
```

**Stop service:**

```bash
sudo systemctl stop attendance.service
```

**Restart service:**

```bash
sudo systemctl restart attendance.service
```

**View logs:**

```bash
sudo journalctl -u attendance.service -n 100
```

**View real-time logs:**

```bash
sudo journalctl -u attendance.service -f
```

## System Management

**Reboot Raspberry Pi:**

```bash
sudo reboot
```

**Shutdown:**

```bash
sudo shutdown -h now
```

**Check temperature:**

```bash
vcgencmd measure_temp
```

**Check system resources:**

```bash
htop
```

Press `q` to quit.

## Database

**View attendance records:**

```bash
sqlite3 /home/pi/attendance_system/database/attendance.db "SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 10;"
```

**View all students:**

```bash
sqlite3 /home/pi/attendance_system/database/attendance.db "SELECT id, name, aruco_id FROM students;"
```

**Exit sqlite:**

```bash
.quit
```

## Backup Database (From Your PC)

**Using PowerShell on your PC:**

```powershell
scp pi@YOUR_PI_IP:/home/pi/attendance_system/database/attendance.db E:\AI\backup\attendance_backup.db
```

## Update Code

**If you modify code on your PC:**

1. **Save changes**
2. **Transfer to Pi:**
   ```powershell
   scp E:\AI\attendance_system\main_attendance.py pi@YOUR_PI_IP:/home/pi/attendance_system/
   ```
3. **Restart service:**
   ```bash
   sudo systemctl restart attendance.service
   ```

---

# 🎉 DEPLOYMENT COMPLETE!

## ✅ What You've Accomplished:

- ✅ Flashed Raspberry Pi OS onto SD card
- ✅ Added your project files during setup
- ✅ Configured WiFi and SSH
- ✅ Updated system and installed dependencies
- ✅ Configured hardware for Raspberry Pi
- ✅ Tested the attendance system
- ✅ Set up auto-start on boot

## 🚀 Your System is Now:

- **Running 24/7** on Raspberry Pi
- **Auto-starting** when Pi boots
- **Ready for attendance** marking
- **Accessible remotely** via SSH

## 📊 Daily Usage:

**Check if running:**

```bash
ssh pi@YOUR_PI_IP
sudo systemctl status attendance.service
```

**View live activity:**

```bash
sudo journalctl -u attendance.service -f
```

**Backup database weekly:**

```powershell
scp pi@YOUR_PI_IP:/home/pi/attendance_system/database/attendance.db E:\AI\backup\attendance_$(Get-Date -Format 'yyyyMMdd').db
```

---

## 🆘 TROUBLESHOOTING

### Can't Find IP Address

- Check router's connected devices list
- Try: `ping attendance-pi.local`
- Connect Ethernet cable temporarily

### SSH Connection Refused

- Wait 3-5 minutes after boot
- Check Pi is powered on (red LED solid)
- Try: `ssh pi@attendance-pi.local`

### LCD Not Displaying

```bash
sudo i2cdetect -y 1
```

Check address (27 or 3F), update config.py

### Camera Not Working

```bash
vcgencmd get_camera
```

Should show: `supported=1 detected=1`

If not, check ribbon cable connection.

### Service Not Starting

```bash
sudo journalctl -u attendance.service -n 50
```

Check error messages in logs.

### System Slow

```bash
vcgencmd measure_temp
```

If over 80°C, add heatsink or fan.

---

## 📞 Quick Reference Card

**IP Address:** ********\_\_\_******** (write yours here)

**SSH Command:** `ssh pi@___________`

**Password:** ********\_\_\_******** (your Pi password)

**View Logs:** `sudo journalctl -u attendance.service -f`

**Restart System:** `sudo systemctl restart attendance.service`

**Reboot Pi:** `sudo reboot`

---

**🎊 Congratulations! Your AI-Powered Attendance System is LIVE! 🎊**

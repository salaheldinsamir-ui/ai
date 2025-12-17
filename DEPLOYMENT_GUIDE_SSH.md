# Raspberry Pi 4 Deployment Guide - HEADLESS SSH SETUP

## AI-Powered Attendance System - Complete SSH-Based Setup

---

## 🎯 WHAT IS THIS GUIDE FOR?

This guide is for setting up your Raspberry Pi **WITHOUT** a monitor, keyboard, or mouse. You'll configure everything remotely from your Windows PC using SSH.

**Best for:**

- ✅ You don't have extra monitor/keyboard/mouse
- ✅ You want to configure everything from your PC
- ✅ You're comfortable with command line
- ✅ **You have OR can get a microSD card reader**

---

## ⚠️ CRITICAL: microSD Card Reader Problem

### YOU NEED A WAY TO WRITE TO THE microSD CARD!

**The Problem:** You can't install the operating system on the Raspberry Pi without first putting it on the microSD card, and you need a way to connect the card to your PC.

### SOLUTIONS (Choose One):

#### Solution 1: Buy a microSD Card Reader (Cheapest - $3-10)

- **Amazon**: Search "microSD card reader USB"
- **Cost**: $3-10
- **Ships**: 1-2 days with Prime
- **Recommended models**:
  - Anker 2-in-1 USB Card Reader (~$8)
  - UGREEN Card Reader (~$7)
  - Generic USB microSD adapter (~$3-5)

**This is the EASIEST solution - just buy one!**

---

#### Solution 2: Use Your Phone/Tablet (If Android)

**If you have an Android phone or tablet:**

1. **Download Raspberry Pi Imager for Android**:

   - Open Google Play Store
   - Search "Raspberry Pi Imager"
   - Install the app

2. **Use OTG Cable**:

   - You need a USB OTG (On-The-Go) adapter
   - Connects USB devices to your phone
   - Cost: $3-5
   - Insert microSD card reader → OTG cable → Phone

3. **Flash the OS**:

   - Follow same steps as PC version
   - Configure WiFi and SSH in settings
   - Flash to microSD card

4. **Transfer project files later via WiFi**

**Note:** iOS doesn't support Raspberry Pi Imager.

---

#### Solution 3: Check Your Laptop for Built-in SD Card Slot

**Many laptops have SD card slots!**

1. **Look at the sides of your laptop**:

   - Some have full-size SD card slots
   - Usually on the side or front edge
   - Looks like a thin slot

2. **If you have full-size SD slot**:
   - You need a **microSD to SD adapter**
   - Usually comes FREE with microSD cards!
   - Insert microSD into adapter → Insert adapter into laptop slot

```
microSD Card → [Insert into SD Adapter] → [Insert into Laptop SD Slot]
     ▼               ▼                          ▼
   ═══╗          ┌────────┐              ┌─────────────┐
   ╚══╝          │░░microSD│              │ [SD Slot]   │
                 │░░░░░░░░░│──────────→   │   Laptop    │
                 └────────┘              └─────────────┘
```

---

#### Solution 4: Ask Friend/Colleague/Computer Shop

- Ask someone with a card reader to flash it for you
- Many computer repair shops will do this for free or $5
- University/school computer labs often have card readers

---

#### Solution 5: Buy Pre-Flashed microSD Card

- Some sellers on Amazon/eBay sell pre-flashed cards with Raspberry Pi OS
- Cost: $15-25 (more expensive)
- Search: "Raspberry Pi OS microSD card pre-installed"
- **Downside**: You still need to configure WiFi/SSH manually by editing files

---

## 🚀 SETUP GUIDE (Assuming You Have microSD Card Reader)

### PART 1: Prepare microSD Card on Your Windows PC

#### Step 1.1: Download Raspberry Pi Imager

1. **On your Windows PC**, open browser
2. Go to: **https://www.raspberrypi.com/software/**
3. Click **"Download for Windows"**
4. Install the downloaded file (`imager_1.x.x.exe`)

#### Step 1.2: Insert microSD Card

1. **Remove microSD card** from package
2. **Insert into microSD card reader**
3. **Plug card reader** into your PC's USB port
4. **Wait for Windows to detect it**

#### Step 1.3: Flash OS with SSH Enabled (CRITICAL SETTINGS)

1. **Open Raspberry Pi Imager**

2. **Click "CHOOSE DEVICE"**:

   - Select: **Raspberry Pi 4**

3. **Click "CHOOSE OS"**:

   - Select: **Raspberry Pi OS (64-bit)**
   - Full version with desktop (NOT Lite)

4. **Click "CHOOSE STORAGE"**:

   - Select your microSD card

5. **Click "NEXT"**

6. **⚠️ CRITICAL: Click "EDIT SETTINGS"**

   This is where you configure SSH and WiFi!

7. **GENERAL Tab** - Fill in ALL these fields:

   ```
   ✅ Set hostname: attendance-pi

   ✅ Set username and password:
      Username: pi
      Password: [Choose a strong password and WRITE IT DOWN!]

   ✅ Configure wireless LAN:
      SSID: [Your WiFi Network Name]
      Password: [Your WiFi Password]
      Country: [Your Country Code - e.g., US, GB, EG, SA]

      ⚠️ IMPORTANT NOTES:
      - Raspberry Pi 4 only supports 2.4GHz WiFi (not 5GHz)
      - Make sure your router has 2.4GHz enabled
      - Use exact WiFi name (case-sensitive!)
      - Double-check password!

   ✅ Set locale settings:
      Time zone: [Your timezone, e.g., Africa/Cairo]
      Keyboard layout: us
   ```

8. **SERVICES Tab** - CRITICAL FOR SSH:

   ```
   ✅ Enable SSH: [CHECK THIS BOX!]
   ● Use password authentication
   ```

9. **Click "SAVE"**

10. **Confirm "YES"** to erase card

11. **Wait 5-15 minutes** for writing and verification

12. **When done**:
    - Click "CONTINUE"
    - **Safely eject** the microSD card
    - Remove from PC

**🎉 Your microSD card is ready for headless setup!**

---

### PART 2: Boot Raspberry Pi (No Monitor Needed)

#### Step 2.1: Physical Setup

1. **Insert microSD card** into Raspberry Pi (bottom slot, metal contacts up)
2. **Connect Ethernet cable** (optional but HIGHLY recommended for first boot):
   - From your router to Raspberry Pi Ethernet port
   - Makes finding the IP address much easier
3. **Connect USB-C power** (LAST!)
4. **Wait 2-3 minutes** for boot

**What's happening:**

- 🔴 Red LED: Power on
- 🟢 Green LED: Blinking = booting and connecting to WiFi
- After ~2-3 minutes: Should be connected and SSH-ready

---

### PART 3: Connect to Raspberry Pi via SSH

#### Step 3.1: Find Raspberry Pi's IP Address

**Method 1: Using Router Admin Page (Most Reliable)**

1. **Open browser on your PC**
2. **Go to your router's admin page**:
   - Common addresses: `192.168.1.1` or `192.168.0.1` or `192.168.100.1`
   - Check router sticker for login details
3. **Login** (common defaults: admin/admin or admin/password)
4. **Find "Connected Devices" or "DHCP Clients"** section
5. **Look for**:
   - Device name: `attendance-pi`
   - Or MAC address starting with: `B8:27:EB`, `DC:A6:32`, or `E4:5F:01` (Raspberry Pi)
6. **Note the IP address** (e.g., `192.168.1.150`)

---

**Method 2: Using Windows Command (Advanced Scan)**

1. **Open PowerShell** (Windows key → type "PowerShell")
2. **Type**:
   ```powershell
   arp -a
   ```
3. **Look for entries** with your network range (e.g., 192.168.1.x)
4. **Try pinging common IPs**:
   ```powershell
   ping attendance-pi.local
   ```
   If this works, you can use `attendance-pi.local` instead of IP!

---

**Method 3: Using Network Scanner App**

1. **Download "Advanced IP Scanner"** (free for Windows)
   - https://www.advanced-ip-scanner.com/
2. **Run scan** on your network
3. **Look for** "Raspberry Pi" or "attendance-pi"

---

#### Step 3.2: Connect via SSH from PowerShell

**What is SSH?**
SSH (Secure Shell) lets you access the Raspberry Pi's command line remotely from your PC. It's like having a Terminal window that controls the Pi.

**Steps:**

1. **Open PowerShell** on your Windows PC:

   - Press **Windows key**
   - Type **"PowerShell"**
   - Click **Windows PowerShell**

2. **Type SSH command** (replace IP with yours):

   ```powershell
   ssh pi@192.168.1.150
   ```

   Or if ping worked:

   ```powershell
   ssh pi@attendance-pi.local
   ```

3. **First connection warning**:

   ```
   The authenticity of host '192.168.1.150' can't be established.
   ECDSA key fingerprint is SHA256:...
   Are you sure you want to continue connecting (yes/no/[fingerprint])?
   ```

   - Type **`yes`** and press Enter

4. **Enter password** (the one you set in Imager):

   ```
   pi@192.168.1.150's password:
   ```

   - Type your password
   - ⚠️ You won't see anything as you type (security feature)
   - Press Enter

5. **SUCCESS! You'll see**:

   ```
   Linux attendance-pi 6.1.0-rpi7-rpi-v8 #1 SMP PREEMPT Debian ...

   The programs included with the Debian GNU/Linux system are free software;
   ...

   pi@attendance-pi:~ $
   ```

**🎉 YOU'RE NOW CONTROLLING THE RASPBERRY PI FROM YOUR PC!**

---

### PART 4: Initial Configuration via SSH

All commands below are typed in your PowerShell window (you're connected via SSH).

#### Step 4.1: Verify System Info

**Check you're connected:**

```bash
hostname
```

Should show: `attendance-pi`

**Check OS version:**

```bash
cat /etc/os-release
```

**Check WiFi connection:**

```bash
ip addr show wlan0
```

Should show an IP address if WiFi is connected.

---

#### Step 4.2: Update System (IMPORTANT!)

**This takes 20-40 minutes - be patient!**

```bash
sudo apt update
```

Wait for package list to update...

```bash
sudo apt upgrade -y
```

This downloads and installs all updates. Takes 20-40 minutes! ☕

**When done, reboot:**

```bash
sudo reboot
```

**SSH connection will close. Wait 2 minutes, then reconnect:**

```powershell
ssh pi@192.168.1.150
```

Enter password again.

---

#### Step 4.3: Enable Required Interfaces

**Open configuration tool:**

```bash
sudo raspi-config
```

**Navigate using keyboard:**

- Arrow keys (↑↓) to move
- Enter to select
- Tab to move between options
- Esc to go back

**Enable these:**

1. **Enable Camera**:

   - Select: `3 Interface Options`
   - Select: `I1 Legacy Camera`
   - Select: `Yes`
   - Press Enter

2. **Enable I2C** (for LCD):

   - Select: `3 Interface Options`
   - Select: `I5 I2C`
   - Select: `Yes`
   - Press Enter

3. **SSH should already be enabled** (you're using it!)

4. **Exit**:
   - Tab to `Finish`
   - Press Enter
   - Select `Yes` to reboot

**Wait 2 minutes, reconnect via SSH:**

```powershell
ssh pi@192.168.1.150
```

---

#### Step 4.4: Install System Dependencies

**Copy and paste each command. Wait for each to finish!**

**Install Python and tools:**

```bash
sudo apt install python3-pip python3-dev python3-venv -y
```

**Install OpenCV and computer vision libraries:**

```bash
sudo apt install -y libopencv-dev python3-opencv libatlas-base-dev libjasper-dev libqtgui4 libqt4-test libhdf5-dev libhdf5-serial-dev
```

**Install I2C tools:**

```bash
sudo apt install -y i2c-tools
```

**Install camera library:**

```bash
sudo apt install -y python3-picamera2
```

**Install GPIO libraries:**

```bash
sudo apt install -y python3-rpi.gpio python3-gpiozero
```

**All dependencies installed! ✅**

---

### PART 5: Transfer Project Files via SSH

#### Step 5.1: Transfer Using SCP from Your PC

**On your Windows PC** (open NEW PowerShell window - keep SSH connection open in other window):

**Transfer entire project folder:**

```powershell
scp -r E:\AI\attendance_system pi@192.168.1.150:/home/pi/
```

**You'll be asked for password:**

- Enter your Pi password
- Wait 2-5 minutes for transfer

**Files transfer with progress shown:**

```
config.py                     100%  1234  123KB/s  00:01
main_attendance.py            100%  5678  567KB/s  00:02
...
```

---

#### Step 5.2: Verify Files Transferred

**In your SSH window (connected to Pi):**

```bash
cd /home/pi/attendance_system
ls -la
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
...
```

**✅ Files are on the Pi!**

---

### PART 6: Install Python Dependencies

**In SSH window:**

```bash
cd /home/pi/attendance_system
```

**Install Python packages (takes 20-30 minutes!):**

```bash
pip install -r requirements.txt
```

**This will install:**

- OpenCV
- DeepFace
- TensorFlow
- And all other dependencies

**⚠️ If you get TensorFlow errors:**

```bash
pip install tensorflow-aarch64
```

---

### PART 7: Configure for Raspberry Pi

**Edit config file:**

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

**Save:**

- Press `Ctrl+O` (letter O)
- Press Enter
- Press `Ctrl+X`

---

### PART 8: Test the System

**Before testing, make sure you've wired all hardware components according to CIRCUIT_GUIDE.md!**

**Run the attendance system:**

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
...
[Init] System initialization complete!
```

**To stop:**

- Press `Ctrl+C`

---

### PART 9: Set Up Auto-Start on Boot

**Create systemd service:**

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

**Save:**

- `Ctrl+O`, Enter, `Ctrl+X`

**Enable service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable attendance.service
sudo systemctl start attendance.service
```

**Check status:**

```bash
sudo systemctl status attendance.service
```

Should show: `active (running)`

**View live logs:**

```bash
sudo journalctl -u attendance.service -f
```

---

## 📱 SSH Management Commands

### Connect to Raspberry Pi:

```powershell
ssh pi@192.168.1.150
```

### Copy files TO Raspberry Pi:

```powershell
scp -r E:\AI\attendance_system\file.py pi@192.168.1.150:/home/pi/attendance_system/
```

### Copy files FROM Raspberry Pi to PC:

```powershell
scp pi@192.168.1.150:/home/pi/attendance_system/database/attendance.db E:\AI\backup\
```

### Copy entire database backup:

```powershell
scp -r pi@192.168.1.150:/home/pi/attendance_system/database E:\AI\backup\
```

### Restart Raspberry Pi:

```bash
sudo reboot
```

### Shutdown Raspberry Pi:

```bash
sudo shutdown -h now
```

### Check system temperature:

```bash
vcgencmd measure_temp
```

### Check system resources:

```bash
htop
```

Press `q` to quit.

---

## 🔧 Useful SSH Tips

### Keep SSH Connection Alive

If your SSH keeps disconnecting, create config file:

**On your Windows PC:**

```powershell
notepad $HOME\.ssh\config
```

**Add:**

```
Host attendance-pi
    HostName 192.168.1.150
    User pi
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

**Save and close.**

**Now you can connect with just:**

```powershell
ssh attendance-pi
```

---

### Use SSH Keys (No Password Needed)

**On your Windows PC:**

1. **Generate SSH key:**

   ```powershell
   ssh-keygen -t rsa -b 4096
   ```

   Press Enter for all prompts (accept defaults)

2. **Copy key to Raspberry Pi:**

   ```powershell
   type $HOME\.ssh\id_rsa.pub | ssh pi@192.168.1.150 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
   ```

   Enter password one last time

3. **Now connect without password:**
   ```powershell
   ssh pi@192.168.1.150
   ```
   No password needed! 🎉

---

## 🆘 Troubleshooting SSH Setup

### Problem: Can't Find Raspberry Pi IP Address

**Solutions:**

1. **Connect Ethernet cable temporarily** - easier to find wired devices
2. **Check router DHCP list** - login to router admin page
3. **Try mDNS hostname:**
   ```powershell
   ping attendance-pi.local
   ```
4. **Use network scanner**: Download "Advanced IP Scanner"

---

### Problem: SSH Connection Refused

**Check:**

1. **Is Pi powered on?** (red LED should be solid)
2. **Is Pi on same network?** (check router)
3. **Did you enable SSH in Imager?** (re-flash if not)
4. **Try hostname instead of IP:**
   ```powershell
   ssh pi@attendance-pi.local
   ```

---

### Problem: WiFi Not Connecting

**Check:**

1. **Router has 2.4GHz enabled** (Pi 4 doesn't support 5GHz)
2. **WiFi password correct** (case-sensitive!)
3. **Country code correct** in Imager settings
4. **Use Ethernet temporarily:**
   - Connect Ethernet cable
   - SSH in
   - Configure WiFi manually:
     ```bash
     sudo raspi-config
     ```
     System Options → Wireless LAN

---

### Problem: "Permission Denied" Errors

**Solutions:**

1. **Add sudo before command:**

   ```bash
   sudo your-command-here
   ```

2. **Check file permissions:**

   ```bash
   ls -la /home/pi/attendance_system
   ```

3. **Fix ownership:**
   ```bash
   sudo chown -R pi:pi /home/pi/attendance_system
   ```

---

### Problem: Package Installation Fails

**Try:**

1. **Update package list:**

   ```bash
   sudo apt update
   ```

2. **Fix broken dependencies:**

   ```bash
   sudo apt --fix-broken install
   ```

3. **Clean package cache:**
   ```bash
   sudo apt clean
   sudo apt autoclean
   ```

---

## 📊 Monitoring System Remotely

### Check Service Status:

```bash
sudo systemctl status attendance.service
```

### View Real-Time Logs:

```bash
sudo journalctl -u attendance.service -f
```

### Check Last 100 Log Lines:

```bash
sudo journalctl -u attendance.service -n 100
```

### Check Database Records:

```bash
sqlite3 /home/pi/attendance_system/database/attendance.db "SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 10;"
```

### Check System Health:

```bash
echo "Temperature: $(vcgencmd measure_temp)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
echo "Uptime: $(uptime -p)"
```

---

## 🎉 DEPLOYMENT COMPLETE!

Your Raspberry Pi is now:

- ✅ Configured headlessly via SSH
- ✅ Running attendance system
- ✅ Auto-starting on boot
- ✅ Accessible remotely from your PC

### Daily Usage:

**Connect to view logs:**

```powershell
ssh pi@192.168.1.150
sudo journalctl -u attendance.service -f
```

**Backup database:**

```powershell
scp pi@192.168.1.150:/home/pi/attendance_system/database/attendance.db E:\AI\backup\attendance_$(Get-Date -Format 'yyyyMMdd').db
```

**Update code:**

1. Edit files on your PC
2. Transfer:
   ```powershell
   scp E:\AI\attendance_system\file.py pi@192.168.1.150:/home/pi/attendance_system/
   ```
3. Restart service:
   ```bash
   sudo systemctl restart attendance.service
   ```

**Your system is live! 🚀**

# Raspberry Pi 4 Deployment Guide

## AI-Powered Attendance System - Complete Setup

---

## 🎓 COMPLETE BEGINNER'S GUIDE - START HERE!

### What is a Raspberry Pi?

A Raspberry Pi is a small, affordable computer (about the size of a credit card) that can run a full operating system. Think of it as a mini-computer that you'll use to run your attendance system 24/7.

### Do I Need to Connect Raspberry Pi to My PC?

**Answer: NO, but you have TWO options:**

#### Option 1: Raspberry Pi as Standalone Computer (EASIEST FOR BEGINNERS)

- Connect Raspberry Pi to its OWN monitor, keyboard, and mouse
- The Pi becomes an independent computer
- You'll set it up just like a new laptop
- **This is what we recommend for first-time setup**

#### Option 2: Headless Setup (Advanced - No Monitor Needed)

- Configure everything via network from your PC
- Requires SSH (remote connection)
- More complex but good if you don't have spare monitor/keyboard
- We'll cover this later in the guide

---

## 📦 What's in Your Raspberry Pi 4 Box?

When you open your Raspberry Pi 4 package, you should see:

- **1x Raspberry Pi 4 Board** (the main computer - green circuit board)
- **That's usually it!** Most other items sold separately

### What You Still Need to Buy:

#### Essential Items (MUST HAVE):

1. **microSD Card**

   - Size: 32GB minimum (64GB recommended)
   - Speed: Class 10 or UHS-I
   - Brand: SanDisk, Samsung, or Kingston recommended
   - 💰 Cost: $8-15
   - Why: This is the Raspberry Pi's "hard drive" - stores the operating system and your files

2. **USB-C Power Supply**

   - Specification: 5V / 3A (15W)
   - Must be USB-C (looks like modern phone charger)
   - Official Raspberry Pi power supply recommended
   - 💰 Cost: $8-12
   - ⚠️ **IMPORTANT**: Using wrong power supply can cause random crashes!

3. **microSD Card Reader**
   - USB adapter to connect microSD card to your PC
   - Most PCs don't have built-in microSD slots
   - 💰 Cost: $5-10
   - Why: Needed to install operating system from your PC

#### For Initial Setup (Choose One):

**Option A: Direct Setup (Recommended for Beginners)** 4. **HDMI Cable**

- Type: **micro HDMI to HDMI**
- ⚠️ NOT regular HDMI! Raspberry Pi 4 uses MICRO HDMI (smaller)
- 💰 Cost: $5-8

5. **Monitor/TV with HDMI Input**
   - Can use your existing computer monitor or TV
   - Must have HDMI port
6. **USB Keyboard**
   - Any USB keyboard works
   - Can use your existing PC keyboard temporarily
7. **USB Mouse**
   - Any USB mouse works
   - Can use your existing PC mouse temporarily

**Option B: Headless Setup (Advanced)**

- Skip monitor/keyboard/mouse
- Need Ethernet cable OR WiFi credentials
- Access via SSH from your PC
- More complex - not recommended for first Pi

#### For the Attendance System Hardware:

8. **Electronic Components** (See CIRCUIT_GUIDE.md for complete list):
   - Pi Camera Module V2 ($25)
   - 2x HC-SR04 Ultrasonic Sensors ($3 each)
   - 16x2 I2C LCD Display ($8)
   - Active Buzzer ($1)
   - Breadboard ($5)
   - Jumper wires ($5)
   - Resistors for voltage dividers ($2)

---

## 🔧 PHYSICAL SETUP GUIDE (Before Turning On)

### Step 1: Understand the Raspberry Pi Ports

Look at your Raspberry Pi 4 board. Here's what each port does:

```
TOP VIEW OF RASPBERRY PI 4:
┌─────────────────────────────────────┐
│  [USB-C Power]               [HDMI0]│ ← micro HDMI port 0
│                              [HDMI1]│ ← micro HDMI port 1
│                                     │
│                        [Audio Jack] │
│  [USB 2.0] [USB 2.0]                │
│                     [Ethernet Port] │
│  [USB 3.0] [USB 3.0]                │
│                                     │
│  [40 GPIO Pins - Two Rows]          │
│                                     │
│         [microSD Card Slot]         │ ← BOTTOM SIDE
└─────────────────────────────────────┘
```

### Step 2: Insert the microSD Card (BEFORE POWERING ON!)

⚠️ **CRITICAL: Insert microSD BEFORE connecting power!**

1. **Locate the microSD slot**: It's on the BOTTOM of the Pi board
2. **Orient the card**: Metal contacts facing UP toward the board
3. **Insert gently**: Push until you hear/feel a small click
4. **It should sit flush** - not sticking out much

```
SIDE VIEW:
                    ┌─────────┐
                    │ Pi Board│
                    └─────────┘
  microSD Card →  ═══╗     ║
                     ╚═════╝
        Push in this direction →
```

### Step 3: Connect Monitor (HDMI)

1. **Get your micro HDMI to HDMI cable**
2. **micro HDMI end** → Plug into **HDMI0** port on Raspberry Pi (the one closer to USB-C power)
3. **HDMI end** → Plug into your monitor/TV
4. **Turn on monitor** and select correct HDMI input

⚠️ **Common Mistake**: Using regular HDMI cable - won't fit! Must be MICRO HDMI.

### Step 4: Connect Keyboard and Mouse

1. **Plug USB keyboard** into any USB port (blue USB 3.0 or black USB 2.0 ports)
2. **Plug USB mouse** into another USB port
3. Order doesn't matter - any ports work

### Step 5: Connect Network (Optional but Recommended)

**Option A: Ethernet (More Reliable)**

- Plug Ethernet cable from your router into the Ethernet port on Pi
- No configuration needed - automatic

**Option B: WiFi**

- Skip for now - we'll configure after first boot
- You'll select WiFi network after Pi starts

### Step 6: Connect Power (LAST STEP!)

⚠️ **DO THIS LAST - As soon as you plug in power, the Pi starts!**

1. **Check everything is connected**:

   - ✅ microSD card inserted
   - ✅ Monitor connected (HDMI)
   - ✅ Keyboard connected (USB)
   - ✅ Mouse connected (USB)
   - ✅ Network (Ethernet or skip for WiFi)

2. **Plug USB-C power cable** into the USB-C port
3. **Plug other end into wall outlet**

**What happens next**:

- 🔴 Red LED lights up (power indicator) - means it's getting power
- 🟢 Green LED flickers (activity indicator) - means it's working
- Monitor shows rainbow screen, then text scrolling (boot messages)
- After 1-3 minutes, you'll see desktop or login screen

⚠️ **If nothing appears on monitor**:

- Check monitor is on correct HDMI input
- Try HDMI1 port instead of HDMI0
- Check micro HDMI cable is fully inserted

---

## 📋 Prerequisites

### Hardware Required

- ✅ Raspberry Pi 4 Model B (4GB RAM)
- ✅ microSD Card (32GB minimum, Class 10)
- ✅ USB-C Power Supply (5V 3A)
- ✅ All components from CIRCUIT_GUIDE.md wired correctly
- ✅ Keyboard, mouse, and monitor (for initial setup)
- ✅ Ethernet cable or WiFi credentials

### Files to Transfer

- Your complete `attendance_system` folder from PC
- Database file: `database/attendance.db` (with enrolled students)
- ArUco marker images (if generated)

---

## 🚀 Step-by-Step Deployment

## PART 1: Prepare Raspberry Pi Operating System

### Step 1.1: Install Operating System on microSD Card (Do This on Your PC)

⚠️ **THIS STEP IS DONE ON YOUR WINDOWS PC, NOT THE RASPBERRY PI!**

The Raspberry Pi doesn't come with an operating system pre-installed. You need to install it on the microSD card using your PC first.

**What is "Flashing"?**
"Flashing" means copying the operating system onto the microSD card. Think of it like installing Windows on a new hard drive, but for Raspberry Pi.

#### Step 1.1a: Download Raspberry Pi Imager (On Your PC)

1. **On your Windows PC**, open web browser
2. Go to: **https://www.raspberrypi.com/software/**
3. Click the **"Download for Windows"** button
4. **Wait for download** (about 20MB, takes 30 seconds to 2 minutes)
5. **Find the downloaded file** (usually in Downloads folder):
   - File name: `imager_1.x.x.exe`
6. **Double-click to install**
7. Click **"Yes"** when Windows asks for permission
8. Follow installation wizard → Click **"Install"** → Click **"Finish"**

#### Step 1.1b: Insert microSD Card into Your PC

1. **Remove microSD card** from its package
2. **Insert into microSD card reader** (the USB adapter)
3. **Plug USB card reader** into your PC's USB port
4. **Windows should detect it** (might hear a sound, see notification)
5. **Don't open any windows that pop up** - just close them

⚠️ **WARNING**: Make sure you select the CORRECT card in next step! Selecting wrong drive will erase it!

#### Step 1.1c: Flash Operating System (Use Raspberry Pi Imager)

1. **Open Raspberry Pi Imager** (should be on your desktop or Start menu)

2. **You'll see 3 buttons:**

   ```
   ┌────────────────────────────────────┐
   │  Raspberry Pi Imager               │
   ├────────────────────────────────────┤
   │  [CHOOSE DEVICE]                   │
   │                                    │
   │  [CHOOSE OS]                       │
   │                                    │
   │  [CHOOSE STORAGE]                  │
   │                                    │
   │              [NEXT]                │
   └────────────────────────────────────┘
   ```

3. **Click "CHOOSE DEVICE"**:

   - Select: **Raspberry Pi 4**
   - Click your selection

4. **Click "CHOOSE OS"**:

   - Select: **Raspberry Pi OS (64-bit)**
   - It should say "Debian Bookworm with desktop" underneath
   - **DO NOT** select Lite version (has no desktop)
   - Click your selection

5. **Click "CHOOSE STORAGE"**:

   - You'll see your microSD card listed (shows size, like "32GB")
   - ⚠️ **DOUBLE CHECK**: Make sure it's your NEW microSD card, not your PC's hard drive!
   - Click your microSD card

6. **Click "NEXT"**

7. **Important Configuration Window Appears:**

   ```
   "Would you like to apply OS customisation settings?"
   ```

   - Click **"EDIT SETTINGS"** (NOT "NO")

8. **GENERAL Tab Settings**:

   - ✅ **Set hostname**: `attendance-pi` (or any name you want)
   - ✅ **Set username and password**:
     - Username: `pi` (recommended)
     - Password: Choose a password you'll remember! Write it down!
   - ✅ **Configure wireless LAN** (WiFi):
     - SSID: Your WiFi network name
     - Password: Your WiFi password
     - Country: Your country (e.g., US, GB, etc.)
     - ⚠️ Note: Raspberry Pi 4 only supports 2.4GHz WiFi, not 5GHz!
   - ✅ **Set locale settings**:
     - Time zone: Your timezone (e.g., America/New_York)
     - Keyboard layout: Your keyboard type (e.g., us)

9. **SERVICES Tab Settings**:

   - ✅ **Enable SSH** (check the box)
   - Select: **"Use password authentication"**
   - This allows you to access Pi remotely later

10. **Click "SAVE"**

11. **Confirm you want to continue:**

    ```
    "All existing data on the SD card will be erased"
    ```

    - Double-check it's the right card
    - Click **"YES"**

12. **Flashing begins!**
    ```
    Progress: Writing... [███████░░░░░] 45%
    ```
    - This takes **5-15 minutes** depending on your PC speed
    - **DO NOT remove the card** while it's writing!
    - You'll see:
      1. "Writing..." (takes most of the time)
      2. "Verifying..." (double-checks everything)
13. **Success Message**:
    ```
    "Raspberry Pi OS has been written to your SD card"
    ```
    - Click **"CONTINUE"**
    - Windows may show error messages about card - **ignore and close them**
    - **Safely eject** the microSD card:
      - Click system tray icon (bottom-right)
      - Click "Eject [card name]"
      - Wait for "Safe to remove" message
    - **Remove microSD card reader** from your PC

**You're done with your PC for now! Next step is on the Raspberry Pi.**

---

### Step 1.2: First Boot of Raspberry Pi

⚠️ **NOW work with your Raspberry Pi hardware**

#### Step 1.2a: Set Up Hardware (Follow "PHYSICAL SETUP GUIDE" above)

If you skipped it, go back to the **PHYSICAL SETUP GUIDE** section and complete:

1. Insert microSD card into Raspberry Pi (BOTTOM slot)
2. Connect HDMI cable to monitor
3. Connect keyboard and mouse (USB ports)
4. Connect power (USB-C) - **LAST STEP!**

#### Step 1.2b: First Boot Process (What You'll See)

1. **Power on** (plug in USB-C power)

2. **Red LED solid** = Getting power ✅
3. **Green LED blinking** = Reading SD card ✅

4. **On your monitor, you'll see**:

   - **Rainbow square** (2 seconds) - means HDMI working
   - **Black screen with white text scrolling** - boot messages
   - **Raspberry Pi logo with progress bar** - loading desktop
   - **Don't touch anything** - let it boot (takes 1-3 minutes first time)

5. **Automatic Configuration**:

   - If you configured WiFi: It connects automatically
   - If you configured SSH: It's enabled automatically
   - If you set username/password: Already configured

6. **Desktop Appears!**:
   ```
   ┌────────────────────────────────────────┐
   │  Menu  |  [Icons]  |  WiFi  Clock     │  ← Top Bar
   ├────────────────────────────────────────┤
   │                                        │
   │     [Wastebasket Icon]                 │
   │                                        │
   │         Raspberry Pi Desktop           │
   │                                        │
   │     (Raspberry Pi wallpaper)           │
   │                                        │
   └────────────────────────────────────────┘
   ```

**🎉 SUCCESS! Your Raspberry Pi is running!**

#### Step 1.2c: Login (If Asked)

If you see a login screen:

- **Username**: `pi` (or what you set in Imager)
- **Password**: (what you set in Imager)
- Press **Enter**

#### Step 1.2d: Check WiFi Connection

Look at **top-right corner** of desktop:

- **WiFi icon with bars** = Connected ✅
- **WiFi icon with X** = Not connected ❌

**If not connected to WiFi:**

1. **Click WiFi icon** (top-right)
2. **Select your network** from dropdown
3. **Enter password**
4. **Click Connect**
5. Wait 10 seconds - should show bars

### Step 1.2: Initial Raspberry Pi Configuration

---

### Step 1.3: Update Raspberry Pi System (IMPORTANT!)

New Raspberry Pi systems need updates. This is like Windows Update.

#### Step 1.3a: Open Terminal

**What is Terminal?**
Terminal is a text-based way to give commands to the Raspberry Pi. It's like typing commands instead of clicking buttons.

**How to open Terminal:**

1. **Click the black icon** at top of screen (looks like **>\_**)
2. OR: Click **Menu** (top-left) → **Accessories** → **Terminal**
3. **Terminal window opens** - you'll see:
   ```
   pi@attendance-pi:~ $
   ```
   This is called a "command prompt" - it's waiting for you to type commands.

#### Step 1.3b: Run System Update

**Type these commands EXACTLY as shown. Press Enter after each line.**

1. **First, update the package list**:

   ```bash
   sudo apt update
   ```

   - Type this and press **Enter**
   - **What it does**: Checks for available updates
   - **You'll see**: Text scrolling (package lists downloading)
   - **Wait until you see prompt again**: `pi@attendance-pi:~ $`

2. **Then, install updates**:

   ```bash
   sudo apt upgrade -y
   ```

   - Type this and press **Enter**
   - **What it does**: Actually installs the updates
   - **The `-y` means "automatically say yes"**
   - **This takes 10-30 minutes!** ☕ Get coffee
   - **You'll see progress bars** and lots of text
   - **Wait until you see**: `pi@attendance-pi:~ $` again

3. **Reboot to apply updates**:
   ```bash
   sudo reboot
   ```
   - Type this and press **Enter**
   - **Raspberry Pi will restart** (screen goes black, then reboots)
   - **Wait 1-2 minutes** for it to boot back up
   - **You'll see desktop again**

**Understanding "sudo":**

- `sudo` means "do this as administrator" (like "Run as Administrator" in Windows)
- You need `sudo` for system changes
- Without `sudo`, you get "Permission denied" errors

---

### Step 1.4: Enable Required Interfaces

Your attendance system needs special features enabled (camera, I2C for LCD).

#### Step 1.4a: Open Configuration Tool

1. **Open Terminal** (click **>\_** icon at top)
2. **Type this command**:
   ```bash
   sudo raspi-config
   ```
3. **Press Enter**
4. **A blue screen menu appears**:
   ```
   ┌─────── Raspberry Pi Configuration Tool ───────┐
   │                                                │
   │  1 System Options      Configure system       │
   │  2 Display Options     Configure display      │
   │  3 Interface Options   Configure connections  │
   │  4 Performance Options Configure performance  │
   │  5 Localisation Options Set locale            │
   │  ...                                           │
   └────────────────────────────────────────────────┘
   ```

**How to navigate this menu:**

- **Arrow keys** (↑↓) to move up/down
- **Enter** to select
- **Tab** key to move between options
- **Esc** to go back

#### Step 1.4b: Enable Camera

1. **Press ↓ arrow** until "3 Interface Options" is highlighted
2. **Press Enter**
3. **Press ↓ arrow** until "I1 Legacy Camera" is highlighted
4. **Press Enter**
5. **You see**: "Would you like the legacy camera interface to be enabled?"
6. **Press Tab** until "Yes" is highlighted
7. **Press Enter**
8. **You see**: "The legacy camera interface is enabled"
9. **Press Enter** to go back

#### Step 1.4c: Enable I2C (for LCD Display)

1. **Should still be in "Interface Options"** - if not, select it again
2. **Press ↓ arrow** until "I5 I2C" is highlighted
3. **Press Enter**
4. **You see**: "Would you like the ARM I2C interface to be enabled?"
5. **Press Tab** until "Yes" is highlighted
6. **Press Enter**
7. **You see**: "The ARM I2C interface is enabled"
8. **Press Enter** to go back

#### Step 1.4d: Enable SSH (for Remote Access)

1. **Should still be in "Interface Options"**
2. **Press ↓ arrow** until "I2 SSH" is highlighted
3. **Press Enter**
4. **You see**: "Would you like the SSH server to be enabled?"
5. **Press Tab** until "Yes" is highlighted
6. **Press Enter**
7. **You see**: "The SSH server is enabled"
8. **Press Enter** to go back

#### Step 1.4e: Exit and Reboot

1. **Press Tab** until "Finish" at bottom is highlighted
2. **Press Enter**
3. **You see**: "Would you like to reboot now?"
4. **Press Tab** until "Yes" is highlighted
5. **Press Enter**
6. **Raspberry Pi reboots** - wait 1-2 minutes

---

### Step 1.5: Install System Dependencies

Now we install the software libraries your attendance system needs.

#### Step 1.5a: Open Terminal Again

After reboot:

1. **Desktop appears**
2. **Click Terminal icon** (**>\_** at top)

#### Step 1.5b: Install Python and Development Tools

**Type each command and press Enter. Wait for each to finish before typing the next!**

1. **Install Python basics**:

   ```bash
   sudo apt install python3-pip python3-dev python3-venv -y
   ```

   - **What it does**: Installs Python 3, pip (package installer), and virtual environment tools
   - **Time**: 2-5 minutes
   - **Watch for**: `pi@attendance-pi:~ $` when done

2. **Install OpenCV and image processing libraries**:

   ```bash
   sudo apt install -y libopencv-dev python3-opencv libatlas-base-dev libjasper-dev libqtgui4 libqt4-test libhdf5-dev libhdf5-serial-dev
   ```

   - **What it does**: Installs computer vision libraries for face recognition
   - **Time**: 5-10 minutes
   - **You might see**: Some "package not found" warnings - ignore them

3. **Install I2C tools** (for LCD):

   ```bash
   sudo apt install -y i2c-tools
   ```

   - **What it does**: Installs tools to communicate with LCD display
   - **Time**: 30 seconds

4. **Install camera libraries**:

   ```bash
   sudo apt install -y python3-picamera2
   ```

   - **What it does**: Installs Python library for Pi Camera
   - **Time**: 1-2 minutes

5. **Install GPIO libraries** (for sensors and buzzer):
   ```bash
   sudo apt install -y python3-rpi.gpio python3-gpiozero
   ```
   - **What it does**: Installs libraries to control GPIO pins (those 40 pins on Pi)
   - **Time**: 30 seconds

**All done!** System dependencies installed ✅

---

## PART 2: Transfer Project Files from Your PC to Raspberry Pi

Now we need to copy your attendance system files from your Windows PC to the Raspberry Pi.

### Step 2.1: Find Your Raspberry Pi's IP Address

**What is an IP Address?**
It's like a phone number for your Raspberry Pi on the network. You need it to transfer files.

#### Step 2.1a: On the Raspberry Pi Terminal

**Type this command**:

```bash
hostname -I
```

**You'll see something like**:

```
192.168.1.150
```

**📝 WRITE THIS DOWN!** This is your Raspberry Pi's IP address.

---

### Step 2.2: Transfer Files (THREE OPTIONS - Choose One)

#### OPTION A: USB Flash Drive Method (EASIEST FOR BEGINNERS)

**Best if:** You have a USB flash drive

**Steps:**

1. **On your Windows PC**:

   - Insert USB flash drive
   - Open File Explorer
   - Navigate to `E:\AI\`
   - **Right-click** `attendance_system` folder
   - Select **Copy**
   - Open USB drive in File Explorer
   - **Right-click empty space** → **Paste**
   - **Wait for copy** to complete (1-2 minutes)
   - **Safely eject USB drive** (right-click drive → Eject)

2. **On your Raspberry Pi**:

   - **Unplug USB drive** from PC
   - **Plug USB drive** into Raspberry Pi USB port
   - **File Manager opens** automatically (shows USB drive contents)
   - If not, click **folder icon** at top of screen
   - **You should see** `attendance_system` folder
   - **Right-click** `attendance_system` folder
   - Select **Copy**
   - **Click "Home" folder** in left sidebar (labeled `pi`)
   - **Right-click empty space** → **Paste**
   - **Wait for copy** (1-2 minutes)
   - **Right-click USB drive icon** on desktop → **Eject**
   - **Unplug USB drive**

3. **Verify files copied**:
   - **Open Terminal**
   - Type:
     ```bash
     ls /home/pi/attendance_system
     ```
   - **You should see** your project files listed:
     ```
     config.py  main_attendance.py  database/  hardware/  ai_modules/  ...
     ```

**✅ FILES TRANSFERRED! Skip to PART 3.**

---

#### OPTION B: Network Transfer Using WinSCP (Windows GUI Tool)

**Best if:** You want a visual file transfer tool

**Steps:**

1. **On your Windows PC**:

   a. **Download WinSCP**:

   - Go to: https://winscp.net/eng/download.php
   - Click "Download WinSCP"
   - Install it

   b. **Open WinSCP**

   c. **Fill in connection details**:

   ```
   File protocol: SFTP
   Host name: [YOUR PI IP ADDRESS from Step 2.1]
   Port number: 22
   User name: pi
   Password: [YOUR PI PASSWORD]
   ```

   Example:

   ```
   Host name: 192.168.1.150
   User name: pi
   Password: yourpassword
   ```

   d. **Click "Login"**

   - First time: "Warning - Potential security breach!" → Click **"Yes"** (accept certificate)
   - You'll see split screen:
     - **Left side** = Your Windows PC
     - **Right side** = Raspberry Pi

   e. **Navigate on LEFT side**: Browse to `E:\AI\attendance_system`

   f. **Navigate on RIGHT side**: Should already be at `/home/pi/`

   g. **Drag `attendance_system` folder** from left pane to right pane

   h. **Wait for transfer** (2-5 minutes)

   - You'll see progress bar
   - Files transfer one by one

   i. **Success!** When progress completes, files are on Pi

2. **Verify on Raspberry Pi**:
   - Open Terminal on Pi
   - Type:
     ```bash
     ls /home/pi/attendance_system
     ```
   - Should see all your files

**✅ FILES TRANSFERRED! Skip to PART 3.**

---

#### OPTION C: Command Line Transfer Using SCP (Advanced)

**Best if:** You're comfortable with command line

**Steps:**

1. **On your Windows PC**:

   a. **Open PowerShell**:

   - Press **Windows key**
   - Type **"PowerShell"**
   - Click **Windows PowerShell**

   b. **Type this command** (replace IP with your Pi's IP from Step 2.1):

   ```powershell
   scp -r E:\AI\attendance_system pi@192.168.1.150:/home/pi/
   ```

   **⚠️ Replace `192.168.1.150` with YOUR Raspberry Pi IP!**

   c. **Press Enter**

   d. **First time you might see**:

   ```
   The authenticity of host '192.168.1.150' can't be established.
   ...
   Are you sure you want to continue connecting (yes/no/[fingerprint])?
   ```

   - Type **`yes`** and press Enter

   e. **Enter your Pi password** when prompted:

   ```
   pi@192.168.1.150's password:
   ```

   - Type your password
   - ⚠️ **You won't see password as you type** - this is normal for security
   - Just type it and press Enter

   f. **Files transfer** (you'll see progress):

   ```
   config.py                     100%  1234  123KB/s  00:01
   main_attendance.py            100%  5678  567KB/s  00:02
   attendance_engine.py          100%  3456  345KB/s  00:01
   ...
   ```

   g. **Wait until you see PowerShell prompt** again:

   ```
   PS E:\AI>
   ```

   Transfer complete!

2. **Verify on Raspberry Pi**:
   - Go to Raspberry Pi
   - Open Terminal
   - Type:
     ```bash
     ls /home/pi/attendance_system
     ```
   - Should see all files

**✅ FILES TRANSFERRED! Continue to PART 3.**

---

## PART 3: Install Python Dependencies

### Step 3.1: Navigate to Project Directory

```bash
cd /home/pi/attendance_system
```

### Step 3.2: Create Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3.3: Install Python Packages

```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install additional Raspberry Pi specific packages
pip install RPLCD RPi.GPIO

# This will take 15-30 minutes due to TensorFlow compilation
```

**If you encounter issues with TensorFlow:**

```bash
# Use pre-built wheel for Raspberry Pi
pip install tensorflow-aarch64
```

---

## PART 4: Configure Hardware

### Step 4.1: Update Configuration File

```bash
nano config.py
```

Change these settings:

```python
# Hardware mode
HARDWARE_MODE = "RASPBERRY_PI"  # Change from "PC"

# Camera configuration
CAMERA_INDEX = 0  # For Pi Camera Module

# Verify GPIO pins match your wiring
ULTRASONIC_SENSOR_1_TRIGGER = 23
ULTRASONIC_SENSOR_1_ECHO = 24
ULTRASONIC_SENSOR_2_TRIGGER = 27
ULTRASONIC_SENSOR_2_ECHO = 22
BUZZER_PIN = 17
LCD_I2C_ADDRESS = 0x27  # May need to change to 0x3F
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 4.2: Test I2C LCD Address

```bash
sudo i2cdetect -y 1
```

You should see something like:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

The number you see (27 or 3F) is your LCD address. Update `config.py` if different.

### Step 4.3: Set GPIO Permissions

```bash
sudo usermod -a -G gpio,i2c,video pi
sudo chmod a+rw /dev/gpiomem
```

**Reboot for changes to take effect:**

```bash
sudo reboot
```

---

## PART 5: Test Individual Components

### Step 5.1: Test Camera

```bash
cd /home/pi/attendance_system

# For Pi Camera Module V2
libcamera-hello --timeout 5000

# Should display camera preview for 5 seconds
```

**If camera not working:**

```bash
# Check camera detection
vcgencmd get_camera
# Should show: supported=1 detected=1

# If not detected, check ribbon cable and enable camera in raspi-config
```

### Step 5.2: Test Ultrasonic Sensors

```bash
python3 << EOF
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG1 = 23
ECHO1 = 24

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

GPIO.output(TRIG1, False)
time.sleep(0.1)

GPIO.output(TRIG1, True)
time.sleep(0.00001)
GPIO.output(TRIG1, False)

pulse_start = time.time()
pulse_end = time.time()

while GPIO.input(ECHO1) == 0:
    pulse_start = time.time()

while GPIO.input(ECHO1) == 1:
    pulse_end = time.time()

distance = (pulse_end - pulse_start) * 17150
print(f"Sensor 1 Distance: {distance:.1f} cm")

GPIO.cleanup()
EOF
```

### Step 5.3: Test LCD Display

```bash
python3 << EOF
from RPLCD.i2c import CharLCD

try:
    lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
    lcd.clear()
    lcd.write_string('Attendance\nSystem Ready')
    print("LCD test successful!")
except Exception as e:
    print(f"LCD Error: {e}")
    print("Try changing address to 0x3F in config.py")
EOF
```

### Step 5.4: Test Buzzer

```bash
python3 << EOF
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

print("Buzzer ON...")
GPIO.output(17, True)
time.sleep(1)
print("Buzzer OFF")
GPIO.output(17, False)

GPIO.cleanup()
EOF
```

---

## PART 6: Run the Attendance System

### Step 6.1: First Test Run

```bash
cd /home/pi/attendance_system
python3 main_attendance.py
```

**What to expect:**

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

[Init] Initializing attendance engine...
[Engine] Loaded 3 students from database

[Init] System initialization complete!

ATTENDANCE SYSTEM ACTIVE
Press 'Ctrl+C' to quit
==================================================
```

### Step 6.2: Test Attendance Flow

1. **System starts in IDLE mode**

   - LCD: "System / Standby Mode"

2. **Approach within 45cm**

   - LCD: "Hold Still / Please..."
   - Hold your face steady for 2.5 seconds

3. **Face Recognition**

   - LCD: "Recognizing / Face..."
   - Then: "Hello / [Your Name]"

4. **Show ArUco Marker**

   - LCD: "Show ArUco / Marker"
   - Hold printed ArUco marker to camera

5. **Success**

   - LCD: "Attendance / Taken!"
   - Buzzer: Success tone (2 beeps)
   - Display for 5 seconds

6. **Return to Ready**
   - LCD: "Attendance / System Ready"

### Step 6.3: Stop the System

```bash
# Press Ctrl+C to stop
# Or if running in background:
pkill -f main_attendance.py
```

---

## PART 7: Set Up Auto-Start on Boot

### Step 7.1: Create Systemd Service

```bash
sudo nano /etc/systemd/system/attendance.service
```

**Paste this configuration:**

```ini
[Unit]
Description=AI-Powered Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/attendance_system
Environment="PATH=/home/pi/attendance_system/venv/bin:/usr/bin"
ExecStart=/home/pi/attendance_system/venv/bin/python3 /home/pi/attendance_system/main_attendance.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**If not using virtual environment, use:**

```ini
ExecStart=/usr/bin/python3 /home/pi/attendance_system/main_attendance.py
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 7.2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable attendance.service

# Start service now
sudo systemctl start attendance.service

# Check status
sudo systemctl status attendance.service
```

**You should see:**

```
● attendance.service - AI-Powered Attendance System
   Loaded: loaded (/etc/systemd/system/attendance.service; enabled)
   Active: active (running) since ...
```

### Step 7.3: Service Management Commands

```bash
# Start service
sudo systemctl start attendance.service

# Stop service
sudo systemctl stop attendance.service

# Restart service
sudo systemctl restart attendance.service

# View logs
sudo journalctl -u attendance.service -f

# View last 50 lines
sudo journalctl -u attendance.service -n 50

# Disable auto-start
sudo systemctl disable attendance.service
```

---

## PART 8: Monitoring and Maintenance

### Step 8.1: View Real-Time Logs

```bash
# Live log viewing
sudo journalctl -u attendance.service -f

# Or view log file if you configured logging
tail -f /home/pi/attendance_system/attendance.log
```

### Step 8.2: Check System Resources

```bash
# CPU and memory usage
htop

# Disk space
df -h

# Temperature
vcgencmd measure_temp
```

### Step 8.3: Database Backup

```bash
# Create backup script
nano /home/pi/backup_attendance.sh
```

Add:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/pi/attendance_system/database/attendance.db \
   /home/pi/backups/attendance_${DATE}.db
echo "Backup created: attendance_${DATE}.db"

# Keep only last 30 days
find /home/pi/backups -name "attendance_*.db" -mtime +30 -delete
```

Make executable:

```bash
chmod +x /home/pi/backup_attendance.sh
mkdir -p /home/pi/backups
```

**Add to crontab for daily backups:**

```bash
crontab -e
```

Add line:

```
0 23 * * * /home/pi/backup_attendance.sh
```

---

## PART 9: Troubleshooting

### Issue: Camera Not Working

**Solution:**

```bash
# Check camera status
vcgencmd get_camera

# If not detected:
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot

# Test camera
libcamera-hello --timeout 5000
```

### Issue: LCD Not Displaying

**Solution:**

```bash
# Check I2C connection
sudo i2cdetect -y 1

# If no device found:
# - Check wiring (SDA to Pin 3, SCL to Pin 5)
# - Check power (VCC to 5V, GND to GND)

# If address is 0x3F instead of 0x27:
nano /home/pi/attendance_system/config.py
# Change: LCD_I2C_ADDRESS = 0x3F
```

### Issue: Ultrasonic Sensors Not Working

**Solution:**

```bash
# CRITICAL: Check voltage dividers!
# Measure voltage at GPIO pin - should be ~3.3V, NOT 5V

# Test manually:
python3 /home/pi/attendance_system/hardware/ultrasonic.py
```

### Issue: Permission Denied Errors

**Solution:**

```bash
sudo usermod -a -G gpio,i2c,video pi
sudo chmod a+rw /dev/gpiomem
sudo reboot
```

### Issue: Service Won't Start

**Solution:**

```bash
# Check service status
sudo systemctl status attendance.service

# View detailed logs
sudo journalctl -u attendance.service -n 100

# Common fixes:
# 1. Check file paths in service file
# 2. Verify python path
# 3. Check file permissions
```

### Issue: TensorFlow/DeepFace Errors

**Solution:**

```bash
# Install TensorFlow for ARM
pip uninstall tensorflow
pip install tensorflow-aarch64

# Or use lighter model
nano config.py
# Change: FACE_MODEL = "OpenFace"  # Lighter than Facenet
```

### Issue: System Slow/Laggy

**Solution:**

```bash
# Check CPU temperature
vcgencmd measure_temp
# If over 80°C, add heatsink or fan

# Reduce face recognition frequency
# Edit attendance_engine.py to skip frames

# Use lower resolution
nano config.py
# Change:
# CAMERA_WIDTH = 320
# CAMERA_HEIGHT = 240
```

---

## PART 10: Optimization Tips

### Tip 1: Reduce Boot Time

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
```

### Tip 2: Increase GPU Memory (for camera)

```bash
sudo raspi-config
# Performance Options → GPU Memory → 256
```

### Tip 3: Enable Swap (if needed)

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Tip 4: Monitor System Health

Create monitoring script:

```bash
nano /home/pi/system_health.sh
```

Add:

```bash
#!/bin/bash
echo "=== System Health Check ==="
echo "Temperature: $(vcgencmd measure_temp)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
echo "Uptime: $(uptime -p)"
```

Make executable:

```bash
chmod +x /home/pi/system_health.sh
```

---

## 🎉 Deployment Complete!

Your attendance system is now:

- ✅ Fully installed on Raspberry Pi 4
- ✅ Configured to auto-start on boot
- ✅ Running with all hardware components
- ✅ Backed up regularly
- ✅ Monitored for health

### Next Steps:

1. Mount hardware in permanent location
2. Adjust camera angle for optimal face capture
3. Position ultrasonic sensors at 45cm distance
4. Test with all enrolled students
5. Monitor logs for first few days
6. Fine-tune detection thresholds if needed

### Access Your System:

```bash
# Via SSH from another computer:
ssh pi@<RASPBERRY_PI_IP>

# Check if running:
sudo systemctl status attendance.service

# View attendance records:
sqlite3 /home/pi/attendance_system/database/attendance.db
SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 10;
.quit
```

---

## 📱 Remote Access (Optional)

### Enable VNC for Remote Desktop

```bash
sudo raspi-config
# Interface Options → VNC → Enable

# Install VNC Viewer on your PC
# Connect to: RASPBERRY_PI_IP:5900
```

### Port Forwarding for External Access

If you want to access from outside your network:

1. Login to your router
2. Forward port 22 (SSH) to Raspberry Pi IP
3. Get your public IP: https://whatismyipaddress.com/
4. Connect: `ssh pi@YOUR_PUBLIC_IP`

**⚠️ Security Note:** Use strong passwords and consider SSH key authentication!

---

## 🆘 Support Contacts

If you need help:

- Check logs: `sudo journalctl -u attendance.service -f`
- Review circuit connections: See CIRCUIT_GUIDE.md
- Test components individually
- Check Raspberry Pi forums: https://forums.raspberrypi.com/

**Your AI-Powered Attendance System is now live! 🚀**

#!/bin/bash
#################################################
# AI-Powered Attendance System - Auto Installer
# For Raspberry Pi 4 Model B
#################################################

set -e  # Exit on any error

echo "=================================================="
echo "AI-POWERED ATTENDANCE SYSTEM - AUTO INSTALLER"
echo "=================================================="
echo ""
echo "This script will:"
echo "  1. Update system packages"
echo "  2. Install system dependencies"
echo "  3. Clone project from GitHub"
echo "  4. Install Python dependencies"
echo "  5. Configure system settings"
echo "  6. Set up auto-start service"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Installation cancelled."
    exit 1
fi

echo ""
echo "=================================================="
echo "STEP 1: Updating System Packages"
echo "=================================================="
sudo apt update
sudo apt upgrade -y

echo ""
echo "=================================================="
echo "STEP 2: Installing System Dependencies"
echo "=================================================="
echo "Installing Python and development tools..."
sudo apt install -y python3-pip python3-dev python3-venv

echo "Installing OpenCV and computer vision libraries..."
sudo apt install -y libopencv-dev python3-opencv \
    libhdf5-dev libopenblas-dev liblapack-dev gfortran

echo "Installing I2C tools..."
sudo apt install -y i2c-tools

echo "Installing camera libraries..."
sudo apt install -y python3-picamera2

echo "Installing GPIO libraries..."
sudo apt install -y python3-rpi.gpio python3-gpiozero

echo "Installing Git..."
sudo apt install -y git

echo ""
echo "=================================================="
echo "STEP 3: Cloning Project from GitHub"
echo "=================================================="
cd /home/pi

# Remove existing directory if it exists
if [ -d "attendance_system" ]; then
    echo "Removing existing attendance_system directory..."
    rm -rf attendance_system
fi

echo "Cloning repository..."
git clone https://github.com/salaheldinsamir-ui/ai.git attendance_system
cd attendance_system

echo ""
echo "=================================================="
echo "STEP 4: Installing Python Dependencies"
echo "=================================================="
echo "This may take 20-40 minutes. Please be patient..."
pip install -r requirements.txt

# If TensorFlow fails, try ARM-specific version
if [ $? -ne 0 ]; then
    echo "Standard installation failed. Trying ARM-specific TensorFlow..."
    pip install tensorflow-aarch64
    pip install -r requirements.txt --no-deps
fi

echo ""
echo "=================================================="
echo "STEP 5: Configuring System Settings"
echo "=================================================="

# Update config.py to Raspberry Pi mode
echo "Setting hardware mode to Raspberry Pi..."
sed -i 's/HARDWARE_MODE = "PC"/HARDWARE_MODE = "RASPBERRY_PI"/' config.py

# Check LCD I2C address
echo "Checking LCD I2C address..."
LCD_ADDR=$(sudo i2cdetect -y 1 | grep -E '27|3f' | awk '{for(i=1;i<=NF;i++) if($i=="27"||$i=="3f") print $i}' | head -n 1)
if [ ! -z "$LCD_ADDR" ]; then
    if [ "$LCD_ADDR" = "3f" ]; then
        echo "Updating LCD address to 0x3F..."
        sed -i 's/LCD_I2C_ADDRESS = 0x27/LCD_I2C_ADDRESS = 0x3F/' config.py
    else
        echo "LCD address is 0x27 (already configured)"
    fi
else
    echo "Warning: No LCD detected on I2C bus. Make sure it's connected."
fi

# Set file permissions
sudo chown -R pi:pi /home/pi/attendance_system
chmod +x /home/pi/attendance_system/*.py

echo ""
echo "=================================================="
echo "STEP 6: Enabling Required Interfaces"
echo "=================================================="
echo "Enabling I2C, Camera, and SSH..."

# Enable I2C
sudo raspi-config nonint do_i2c 0

# Enable Legacy Camera
sudo raspi-config nonint do_legacy 0

# Enable SSH (should already be enabled but ensure it)
sudo raspi-config nonint do_ssh 0

echo ""
echo "=================================================="
echo "STEP 7: Creating Auto-Start Service"
echo "=================================================="
echo "Creating systemd service..."

sudo tee /etc/systemd/system/attendance.service > /dev/null <<EOF
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
EOF

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling attendance service..."
sudo systemctl enable attendance.service

echo ""
echo "=================================================="
echo "INSTALLATION COMPLETE!"
echo "=================================================="
echo ""
echo "✅ System packages updated"
echo "✅ Dependencies installed"
echo "✅ Project cloned from GitHub"
echo "✅ Python packages installed"
echo "✅ Configuration updated for Raspberry Pi"
echo "✅ Auto-start service created and enabled"
echo ""
echo "=================================================="
echo "IMPORTANT: NEXT STEPS"
echo "=================================================="
echo ""
echo "1. REBOOT your Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, wire your hardware components:"
echo "   - See CIRCUIT_GUIDE.md for wiring instructions"
echo "   - Connect: Camera, LCD, Ultrasonic sensors, Buzzer"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status attendance.service"
echo ""
echo "4. View live logs:"
echo "   sudo journalctl -u attendance.service -f"
echo ""
echo "5. Manual test (before hardware wired):"
echo "   cd /home/pi/attendance_system"
echo "   python3 main_attendance.py"
echo ""
echo "=================================================="
echo "PROJECT LOCATION: /home/pi/attendance_system"
echo "=================================================="
echo ""
read -p "Reboot now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Rebooting..."
    sudo reboot
else
    echo "Please reboot manually with: sudo reboot"
fi

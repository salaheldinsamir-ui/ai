#!/bin/bash
# Setup script for Attendance System with Virtual Environment

echo "=========================================="
echo "ATTENDANCE SYSTEM - SETUP"
echo "=========================================="

# Install python3-venv if needed
echo "Checking for python3-venv..."
if ! dpkg -l | grep -q python3-venv; then
    echo "Installing python3-venv..."
    sudo apt update
    sudo apt install -y python3-venv python3-full
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

python3 -m venv venv
echo "✓ Virtual environment created"

# Activate and install packages
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing packages (this may take 10-15 minutes)..."
pip install -r requirements.txt

# Run tests
echo ""
echo "=========================================="
echo "TESTING INSTALLATION"
echo "=========================================="
python3 test_setup.py

echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Fix camera memory: sudo raspi-config"
echo "   Go to: Performance Options > GPU Memory > 128"
echo "   Then: sudo reboot"
echo ""
echo "2. After reboot, test camera:"
echo "   source venv/bin/activate"
echo "   python3 test_camera.py"
echo ""
echo "3. Run the system:"
echo "   source venv/bin/activate"
echo "   python3 enroll_students.py"
echo "   python3 main_attendance.py"

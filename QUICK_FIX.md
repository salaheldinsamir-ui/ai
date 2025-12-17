# Quick Fix Instructions

## Run these commands on your Raspberry Pi:

### Step 1: Setup Virtual Environment & Install Packages

```bash
cd ~/ai
bash setup_venv.sh
```

This will take 10-15 minutes. Wait for it to complete.

---

### Step 2: Fix Camera Memory Issue

```bash
sudo raspi-config
```

**Navigate to:**

- Performance Options → GPU Memory → Enter `128` or `256`
- Finish → Yes (reboot)

---

### Step 3: After Reboot - Test Everything

```bash
cd ~/ai
source venv/bin/activate
python3 test_camera.py
python3 test_setup.py
```

All tests should pass now.

---

### Step 4: Run the System

```bash
cd ~/ai
source venv/bin/activate

# Enroll students first
python3 enroll_students.py

# Then run attendance system
python3 main_attendance.py
```

---

## Quick Reference

**Always activate venv before running Python:**

```bash
source venv/bin/activate
```

**To deactivate when done:**

```bash
deactivate
```

---

## If Step 1 Fails

If `bash setup_venv.sh` doesn't work, do it manually:

```bash
# Install venv
sudo apt install python3-venv python3-full

# Create environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

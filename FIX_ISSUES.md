# Fixing Setup Issues

Based on your test results, here's how to fix each issue:

## 1. Install Missing Packages ⚠️

### Issue

`deepface` and `tensorflow` are not installed.

### Solution

```bash
# Install the missing packages
pip3 install deepface tensorflow

# Or install all requirements
pip3 install -r requirements.txt
```

**Note:** On Raspberry Pi, tensorflow might take a while to install. If it fails, try:

```bash
# For Raspberry Pi OS (older version)
pip3 install tensorflow==2.11.0

# Or use TensorFlow Lite
pip3 install tflite-runtime
```

## 2. Fix Camera Access Issues 📷

### Issue

```
Failed to allocate required memory
Failed to read frame from camera
```

This is a common Raspberry Pi camera issue with GStreamer/V4L2.

### Solutions

**Option A: Increase GPU Memory (Recommended)**

```bash
sudo raspi-config
# Navigate to: Performance Options > GPU Memory
# Set to at least 128MB (256MB recommended)
# Reboot: sudo reboot
```

**Option B: Use Legacy Camera Support**

```bash
sudo raspi-config
# Navigate to: Interface Options > Legacy Camera
# Enable it
# Reboot: sudo reboot
```

**Option C: Try Different Camera Index**

```bash
python3 test_camera.py
```

This will test different camera indices and tell you which one works.

**Option D: Disable GStreamer Backend**

Edit [config.py](config.py) and add:

```python
CAMERA_BACKEND = "V4L2"  # or "LEGACY"
```

Then update [hardware/camera.py](hardware/camera.py) to use:

```python
import cv2
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
```

## 3. Face Detection Fixed ✅

The face detection error (`module 'cv2' has no attribute 'data'`) has been fixed in [ai/face_detector.py](ai/face_detector.py).

The updated code now searches multiple possible locations for the Haar Cascade file.

## 4. Testing After Fixes

Run the tests again in this order:

### Step 1: Install packages

```bash
pip3 install deepface tensorflow
```

### Step 2: Test camera

```bash
python3 test_camera.py
```

### Step 3: Run full setup test

```bash
python3 test_setup.py
```

### Step 4: If everything passes, run the main program

```bash
python3 main_attendance.py
```

## Common Issues & Troubleshooting

### TensorFlow Installation Fails

```bash
# Check your Python version
python3 --version

# For Python 3.11+, use:
pip3 install tensorflow==2.15.0

# For older Raspberry Pi (1GB RAM or less):
pip3 install tflite-runtime
# Then edit ai/face_recognition.py to use tflite instead
```

### Camera Still Not Working

1. Check if camera is enabled:

   ```bash
   vcgencmd get_camera
   ```

   Should show: `supported=1 detected=1`

2. Test with raspistill:

   ```bash
   raspistill -o test.jpg
   ```

3. Check camera is not in use:

   ```bash
   sudo fuser /dev/video0
   ```

4. Try with different OpenCV backends:
   ```python
   # In your code
   cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
   # or
   cap = cv2.VideoCapture(0, cv2.CAP_ANY)
   ```

### Memory Issues

If you see "Failed to allocate required memory":

1. Close other applications
2. Increase GPU memory (see Option A above)
3. Reduce camera resolution in config.py:
   ```python
   CAMERA_WIDTH = 640
   CAMERA_HEIGHT = 480
   ```

## Next Steps

Once all tests pass:

1. ✅ Enroll students: `python3 enroll_students.py`
2. ✅ Run attendance system: `python3 main_attendance.py`
3. ✅ Check logs for any runtime errors

## Need More Help?

If issues persist:

1. Share the output of: `python3 test_setup.py`
2. Share the output of: `python3 test_camera.py`
3. Share your system info:
   ```bash
   cat /etc/os-release
   python3 --version
   pip3 list | grep -E "opencv|numpy|tensorflow|deepface"
   ```

"""Quick camera test script"""
import cv2

print("Testing available cameras...")

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✓ Camera {i} works! Resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print(f"✗ Camera {i} opens but can't read frames (likely in use by another app)")
        cap.release()
    else:
        print(f"✗ Camera {i} not available")

print("\nIf a camera works, update CAMERA_INDEX in config.py to that number.")

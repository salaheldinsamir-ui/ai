"""
Quick test to verify ArUco detection is working
"""
import cv2
import numpy as np
from ai.aruco_detector import ArucoDetector

# Initialize detector
detector = ArucoDetector(dictionary="DICT_4X4_50")

# Generate test ArUco markers (IDs 0, 1, 2)
print("Generating test ArUco markers...")
for marker_id in [0, 1, 2]:
    test_marker = detector.generate_marker(marker_id, size=400)
    # Convert to BGR for saving
    test_marker_bgr = cv2.cvtColor(test_marker, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(f"aruco_marker_{marker_id}.png", test_marker_bgr)
    print(f"✓ Saved aruco_marker_{marker_id}.png")

print("\n✓ ArUco markers generated successfully!")
print("Print these markers and hold them up to the camera.")

# Now test with camera
print("\n" + "="*50)
print("Testing ArUco detection with camera...")
print("Hold up the printed ArUco marker to the camera")
print("Press 'q' to quit")
print("="*50)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read camera")
        break
    
    # Detect markers
    marker_ids, corners = detector.detect_markers(frame)
    
    # Draw detection results
    display = frame.copy()
    if len(marker_ids) > 0:
        display = detector.draw_markers(display, corners, np.array(marker_ids).reshape(-1, 1))
        cv2.putText(display, f"Detected: {marker_ids}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(display, "No ArUco detected", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow("ArUco Test", display)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nTest complete!")

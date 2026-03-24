"""
Test script to verify system setup and dependencies
"""
import sys


def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    
    packages = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "deepface": "deepface",
        "tensorflow": "tensorflow",
    }
    
    failed = []
    
    for package, pip_name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {pip_name}")
        except ImportError:
            print(f"  ✗ {pip_name} - NOT INSTALLED")
            failed.append(pip_name)
            
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Install with: pip install " + " ".join(failed))
        return False
    else:
        print("\n✓ All packages installed!")
        return True


def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    # First try picamera2 (Raspberry Pi Camera)
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.start()
        frame = cam.capture_array()
        cam.stop()
        print(f"  ✓ Pi Camera working! Resolution: {frame.shape[1]}x{frame.shape[0]}")
        return True
    except Exception as e:
        pass  # Try OpenCV next
    
    # Fall back to OpenCV (USB webcam / PC)
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("  ✗ Failed to open camera")
            return False
            
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"  ✓ Camera working! Resolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
        else:
            print("  ✗ Failed to read frame from camera")
            return False
            
    except Exception as e:
        print(f"  ✗ Camera error: {e}")
        return False


def test_database():
    """Test database creation"""
    print("\nTesting database...")
    
    try:
        from database.db_manager import DatabaseManager
        import os
        
        test_db_path = os.path.join(os.path.dirname(__file__), "database", "test_attendance.db")
        db = DatabaseManager(test_db_path)
        
        # Try adding a test student
        import numpy as np
        test_embedding = np.random.rand(128)
        
        student_id = db.add_student("Test Student", 999, test_embedding)
        
        if student_id:
            print(f"  ✓ Database working! Test student ID: {student_id}")
            
            # Clean up
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
                
            return True
        else:
            print("  ✗ Failed to add test student")
            return False
            
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_face_detection():
    """Test face detection"""
    print("\nTesting face detection...")
    
    try:
        from ai.face_detector import FaceDetector
        import cv2
        import numpy as np
        
        detector = FaceDetector()
        
        # Create a simple test image (blank image with proper dimensions)
        test_img = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # Test face detection on the image (will return empty, but that's OK for testing)
        faces = detector.detect_faces(test_img)
            
        print("  ✓ Face detector initialized!")
        return True
        
    except Exception as e:
        print(f"  ✗ Face detection error: {e}")
        return False


def test_aruco():
    """Test ArUco detection"""
    print("\nTesting ArUco detection...")
    
    try:
        from ai.aruco_detector import ArucoDetector
        
        detector = ArucoDetector()
        marker = detector.generate_marker(0, 200)
        
        if marker is not None:
            print("  ✓ ArUco detector working!")
            return True
        else:
            print("  ✗ Failed to generate marker")
            return False
            
    except Exception as e:
        print(f"  ✗ ArUco error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*50)
    print("ATTENDANCE SYSTEM - SETUP TEST")
    print("="*50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Camera Access", test_camera),
        ("Database", test_database),
        ("Face Detection", test_face_detection),
        ("ArUco Detection", test_aruco),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results.append((test_name, False))
            
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        
    print("="*50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python enroll_students.py")
        print("2. Run: python main_attendance.py")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        
    print("="*50)


if __name__ == "__main__":
    main()

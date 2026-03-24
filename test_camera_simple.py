"""
Simple camera test to diagnose camera issues
"""
import time

def test_camera():
    print("="*50)
    print("SIMPLE CAMERA TEST")
    print("="*50)
    
    try:
        from picamera2 import Picamera2
        
        print("\n[1/4] Initializing Picamera2...")
        camera = Picamera2()
        
        print("[2/4] Configuring camera...")
        config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        camera.configure(config)
        
        print("[3/4] Starting camera...")
        camera.start()
        
        print("[4/4] Waiting 2 seconds for warmup...")
        time.sleep(2)
        
        print("\n[Test] Capturing 5 frames...")
        for i in range(5):
            try:
                frame = camera.capture_array()
                print(f"  Frame {i+1}: SUCCESS - Shape: {frame.shape}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  Frame {i+1}: FAILED - {e}")
                
        print("\n[Cleanup] Stopping camera...")
        camera.stop()
        camera.close()
        
        print("\n✓ Camera test PASSED!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n✗ Camera test FAILED: {e}")
        print("="*50)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_camera()

"""
Camera Module - Abstract interface for PC and Raspberry Pi cameras
"""
import cv2
import numpy as np


class Camera:
    """Abstract camera interface supporting PC webcam and Raspberry Pi camera"""
    
    def __init__(self, mode="PC", camera_index=0, width=640, height=480):
        """
        Initialize camera
        
        Args:
            mode: "PC" or "RASPBERRY_PI"
            camera_index: Camera index (for PC)
            width: Frame width
            height: Frame height
        """
        self.mode = mode
        self.width = width
        self.height = height
        self.camera = None
        self.is_running = False
        
        if mode == "PC":
            self._init_pc_camera(camera_index)
        elif mode == "RASPBERRY_PI":
            self._init_pi_camera()
        else:
            raise ValueError(f"Invalid camera mode: {mode}")
            
    def _init_pc_camera(self, camera_index):
        """Initialize PC webcam using OpenCV"""
        self.camera = cv2.VideoCapture(camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if not self.camera.isOpened():
            raise RuntimeError("Failed to open PC camera")
        
        self.is_running = True
        print(f"[Camera] PC webcam initialized: {self.width}x{self.height}")
        
    def _init_pi_camera(self):
        """Initialize Raspberry Pi camera"""
        try:
            from picamera2 import Picamera2
            import time
            
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            
            # Give camera time to warm up
            time.sleep(2)
            
            self.is_running = True
            print(f"[Camera] Raspberry Pi camera initialized: {self.width}x{self.height}")
            
        except ImportError:
            print("[Camera] Warning: picamera2 not available, falling back to PC camera")
            self._init_pc_camera(0)
        except Exception as e:
            print(f"[Camera] Error initializing Pi camera: {e}")
            raise
            
    def read_frame(self):
        """
        Read a frame from the camera
        
        Returns:
            Numpy array (BGR format) or None if failed
        """
        if not self.is_running:
            return None
            
        if self.mode == "PC":
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                return None
                
        elif self.mode == "RASPBERRY_PI":
            try:
                frame = self.camera.capture_array()
                # Convert RGB to BGR for OpenCV compatibility
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame_bgr
            except Exception as e:
                print(f"[Camera] Error reading Pi camera: {e}")
                return None
    
    def stop(self):
        """Stop camera (for standby mode)"""
        if not self.is_running:
            return
            
        if self.mode == "RASPBERRY_PI" and self.camera:
            try:
                self.camera.stop()
                self.is_running = False
                print("[Camera] Camera stopped (standby)")
            except Exception as e:
                print(f"[Camera] Error stopping: {e}")
        else:
            self.is_running = False
            print("[Camera] Camera stopped (simulated)")
    
    def start(self):
        """Start camera (wake from standby)"""
        if self.is_running:
            return
            
        if self.mode == "RASPBERRY_PI" and self.camera:
            try:
                self.camera.start()
                time.sleep(1)  # Brief warmup
                self.is_running = True
                print("[Camera] Camera started")
            except Exception as e:
                print(f"[Camera] Error starting: {e}")
        else:
            self.is_running = True
            print("[Camera] Camera started (simulated)")
                
    def release(self):
        """Release camera resources"""
        if self.mode == "PC":
            if self.camera:
                self.camera.release()
                
        elif self.mode == "RASPBERRY_PI":
            if self.camera:
                try:
                    self.camera.stop()
                    self.camera.close()
                except Exception as e:
                    print(f"[Camera] Error releasing: {e}")
        
        self.is_running = False
        print("[Camera] Camera released")
        
    def is_opened(self):
        """Check if camera is opened"""
        if self.mode == "PC":
            return self.camera and self.camera.isOpened()
        elif self.mode == "RASPBERRY_PI":
            return self.camera is not None
        return False

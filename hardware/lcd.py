"""
LCD Display Module - Display messages and status
"""
import time


class LCDDisplay:
    """LCD display for showing attendance status and messages"""
    
    def __init__(self, mode="PC", i2c_address=0x27, rows=2, cols=16):
        """
        Initialize LCD display
        
        Args:
            mode: "PC" or "RASPBERRY_PI"
            i2c_address: I2C address of LCD (Raspberry Pi only)
            rows: Number of rows
            cols: Number of columns
        """
        self.mode = mode
        self.i2c_address = i2c_address
        self.rows = rows
        self.cols = cols
        self.lcd = None
        
        if mode == "RASPBERRY_PI":
            self._init_lcd()
        else:
            print(f"[LCD] PC simulation mode - displaying to terminal")
            
    def _init_lcd(self):
        """Initialize LCD for Raspberry Pi"""
        try:
            from RPLCD.i2c import CharLCD
            
            self.lcd = CharLCD(
                i2c_expander='PCF8574',
                address=self.i2c_address,
                port=1,
                cols=self.cols,
                rows=self.rows,
                backlight_enabled=True  # Ensure backlight is on
            )
            
            self.lcd.clear()
            time.sleep(0.1)  # Small delay after clear
            # Test write to LCD
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string("LCD Ready!")
            print(f"[LCD] Raspberry Pi LCD initialized (Address: {hex(self.i2c_address)})")
            
        except ImportError as e:
            print(f"[LCD] Warning: RPLCD not available ({e}), using simulation mode")
            print("[LCD] Install with: pip install RPLCD")
            self.mode = "PC"
        except Exception as e:
            print(f"[LCD] Error initializing LCD: {e}")
            print(f"[LCD] Check I2C address with: sudo i2cdetect -y 1")
            self.mode = "PC"
            self.lcd = None
            
    def display_message(self, line1, line2=""):
        """
        Display message on LCD
        
        Args:
            line1: First line text
            line2: Second line text (optional)
        """
        # Always print to terminal for debugging
        print(f"[LCD Display] Line1: {line1} | Line2: {line2}")
        
        if self.mode == "PC" or self.lcd is None:
            # Simulate LCD display in terminal
            print("="*20)
            print(f"| {line1[:self.cols].center(self.cols)} |")
            if line2:
                print(f"| {line2[:self.cols].center(self.cols)} |")
            print("="*20)
            
        elif self.mode == "RASPBERRY_PI" and self.lcd:
            try:
                self.lcd.clear()
                time.sleep(0.05)  # Small delay after clear
                self.lcd.cursor_pos = (0, 0)
                self.lcd.write_string(line1[:self.cols])
                
                if line2:
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(line2[:self.cols])
                    
            except Exception as e:
                print(f"[LCD] Error displaying message: {e}")
                
    def clear(self):
        """Clear LCD display"""
        if self.mode == "PC":
            print("[LCD] Display cleared")
            
        elif self.mode == "RASPBERRY_PI" and self.lcd:
            try:
                self.lcd.clear()
            except Exception as e:
                print(f"[LCD] Error clearing display: {e}")
                
    def display_welcome(self):
        """Display welcome message"""
        self.display_message("Attendance", "System Ready")
        
    def display_success(self, name):
        """Display success message with student name"""
        self.display_message("Welcome!", name)
        
    def display_error(self, error_type):
        """Display error message"""
        error_messages = {
            "no_face": ("Error", "No face detected"),
            "multiple_faces": ("Error", "Multiple faces"),
            "no_aruco": ("Error", "Show ArUco tag"),
            "not_recognized": ("Error", "Not recognized"),
            "already_marked": ("Already marked", "today"),
            "mismatch": ("Error", "Face/Tag mismatch"),
            "distance": ("Error", "Check distance")
        }
        
        message = error_messages.get(error_type, ("Error", "Unknown"))
        self.display_message(message[0], message[1])
        
    def cleanup(self):
        """Clean up LCD resources"""
        if self.mode == "RASPBERRY_PI" and self.lcd:
            try:
                self.lcd.clear()
                self.lcd.close()
                print("[LCD] LCD cleaned up")
            except:
                pass

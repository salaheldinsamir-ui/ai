"""
Buzzer Module - Audio feedback for attendance system
"""
import time


class Buzzer:
    """Buzzer for audio feedback"""
    
    def __init__(self, mode="PC", pin=17):
        """
        Initialize buzzer
        
        Args:
            mode: "PC" or "RASPBERRY_PI"
            pin: GPIO pin for buzzer (Raspberry Pi only)
        """
        self.mode = mode
        self.pin = pin
        self.gpio = None
        
        if mode == "RASPBERRY_PI":
            self._init_gpio()
        else:
            print(f"[Buzzer] PC simulation mode - using audio simulation")
            
    def _init_gpio(self):
        """Initialize GPIO for Raspberry Pi"""
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, False)
            
            print(f"[Buzzer] Raspberry Pi GPIO initialized (Pin: {self.pin})")
            
        except ImportError:
            print("[Buzzer] Warning: RPi.GPIO not available, using simulation mode")
            self.mode = "PC"
            
    def beep(self, duration=0.2):
        """
        Single beep
        
        Args:
            duration: Beep duration in seconds
        """
        if self.mode == "PC":
            print(f"[Buzzer] BEEP ({duration}s)")
            time.sleep(duration)
            
        elif self.mode == "RASPBERRY_PI" and self.gpio:
            try:
                self.gpio.output(self.pin, True)
                time.sleep(duration)
                self.gpio.output(self.pin, False)
            except Exception as e:
                print(f"[Buzzer] Error: {e}")
                
    def success_tone(self):
        """Play success tone (2 short beeps)"""
        print("[Buzzer] ✓ SUCCESS TONE")
        self.beep(0.1)
        time.sleep(0.05)
        self.beep(0.1)
        
    def error_tone(self):
        """Play error tone (1 long beep)"""
        print("[Buzzer] ✗ ERROR TONE")
        self.beep(0.5)
        
    def warning_tone(self):
        """Play warning tone (3 quick beeps)"""
        print("[Buzzer] ⚠ WARNING TONE")
        for _ in range(3):
            self.beep(0.08)
            time.sleep(0.05)
            
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.mode == "RASPBERRY_PI" and self.gpio:
            try:
                self.gpio.output(self.pin, False)
                self.gpio.cleanup([self.pin])
                print("[Buzzer] GPIO cleaned up")
            except:
                pass

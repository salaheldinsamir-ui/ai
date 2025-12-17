"""
Ultrasonic Sensor Module - Distance measurement for presence detection
"""
import time


class UltrasonicSensor:
    """Ultrasonic sensor for distance measurement and presence detection"""
    
    def __init__(self, mode="PC", trigger_pin=None, echo_pin=None):
        """
        Initialize ultrasonic sensor
        
        Args:
            mode: "PC" or "RASPBERRY_PI"
            trigger_pin: GPIO pin for trigger (Raspberry Pi only)
            echo_pin: GPIO pin for echo (Raspberry Pi only)
        """
        self.mode = mode
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.gpio = None
        
        if mode == "RASPBERRY_PI":
            self._init_gpio()
        else:
            print(f"[Ultrasonic] PC simulation mode - returning simulated distances")
            
    def _init_gpio(self):
        """Initialize GPIO for Raspberry Pi"""
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            
            # Ensure trigger is low
            GPIO.output(self.trigger_pin, False)
            time.sleep(0.1)
            
            print(f"[Ultrasonic] Raspberry Pi GPIO initialized (Trigger: {self.trigger_pin}, Echo: {self.echo_pin})")
            
        except ImportError:
            print("[Ultrasonic] Warning: RPi.GPIO not available, using simulation mode")
            self.mode = "PC"
            
    def measure_distance(self):
        """
        Measure distance in centimeters
        
        Returns:
            Distance in cm or None if measurement failed
        """
        if self.mode == "PC":
            # Simulate distance for PC testing
            # Return a value within valid range (30-100 cm)
            import random
            return random.uniform(40, 80)
            
        elif self.mode == "RASPBERRY_PI":
            try:
                # Send trigger pulse
                self.gpio.output(self.trigger_pin, True)
                time.sleep(0.00001)  # 10 microseconds
                self.gpio.output(self.trigger_pin, False)
                
                # Wait for echo
                pulse_start = time.time()
                timeout = pulse_start + 0.1  # 100ms timeout
                
                while self.gpio.input(self.echo_pin) == 0:
                    pulse_start = time.time()
                    if pulse_start > timeout:
                        return None
                        
                pulse_end = time.time()
                timeout = pulse_end + 0.1
                
                while self.gpio.input(self.echo_pin) == 1:
                    pulse_end = time.time()
                    if pulse_end > timeout:
                        return None
                        
                # Calculate distance
                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 17150  # Speed of sound = 34300 cm/s
                distance = round(distance, 2)
                
                return distance
                
            except Exception as e:
                print(f"[Ultrasonic] Error measuring distance: {e}")
                return None
                
    def check_presence(self, min_distance=30, max_distance=100):
        """
        Check if presence is detected within valid range
        
        Args:
            min_distance: Minimum valid distance (cm)
            max_distance: Maximum valid distance (cm)
            
        Returns:
            True if presence detected within range, False otherwise
        """
        distance = self.measure_distance()
        
        if distance is None:
            return False
            
        is_present = min_distance <= distance <= max_distance
        
        return is_present
        
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.mode == "RASPBERRY_PI" and self.gpio:
            try:
                self.gpio.cleanup([self.trigger_pin, self.echo_pin])
                print("[Ultrasonic] GPIO cleaned up")
            except:
                pass

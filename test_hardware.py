"""
Simple hardware test - LCD and Buzzer
Tests hardware components independently before running main system
"""
import time
import sys

def test_i2c():
    """Test I2C bus and find LCD address"""
    print("\n" + "="*50)
    print("TESTING I2C BUS")
    print("="*50)
    
    try:
        import smbus
        bus = smbus.SMBus(1)
        
        print("\nScanning I2C bus for devices...")
        devices = []
        for address in range(0x03, 0x78):
            try:
                bus.read_byte(address)
                devices.append(address)
                print(f"  Found device at: 0x{address:02X}")
            except:
                pass
        
        if not devices:
            print("  ✗ No I2C devices found!")
            print("\nTroubleshooting:")
            print("  1. Check I2C is enabled: sudo raspi-config")
            print("  2. Check wiring: SDA, SCL, VCC, GND")
            print("  3. Run: sudo i2cdetect -y 1")
            return None
        else:
            print(f"\n✓ Found {len(devices)} I2C device(s)")
            return devices[0]  # Return first device
            
    except ImportError:
        print("✗ smbus not available - install with: sudo apt install python3-smbus")
        return None
    except Exception as e:
        print(f"✗ I2C test failed: {e}")
        return None

def test_lcd(i2c_address=0x27):
    """Test LCD display"""
    print("\n" + "="*50)
    print(f"TESTING LCD at address 0x{i2c_address:02X}")
    print("="*50)
    
    try:
        from RPLCD.i2c import CharLCD
        
        print("\n[1/4] Initializing LCD...")
        lcd = CharLCD(
            i2c_expander='PCF8574',
            address=i2c_address,
            port=1,
            cols=16,
            rows=2
        )
        
        print("[2/4] Clearing LCD...")
        lcd.clear()
        time.sleep(0.5)
        
        print("[3/4] Writing test message...")
        lcd.cursor_pos = (0, 0)
        lcd.write_string("LCD Test")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Working!")
        
        print("[4/4] LCD should now display:")
        print("  Line 1: LCD Test")
        print("  Line 2: Working!")
        
        time.sleep(3)
        
        print("\n[5/4] Clearing LCD...")
        lcd.clear()
        lcd.close()
        
        print("\n✓ LCD test PASSED!")
        return True
        
    except ImportError:
        print("\n✗ RPLCD not installed!")
        print("Install with: pip install RPLCD")
        return False
    except Exception as e:
        print(f"\n✗ LCD test FAILED: {e}")
        print("\nTroubleshooting:")
        print(f"  1. Try different I2C address (0x3F instead of 0x{i2c_address:02X})")
        print("  2. Check wiring: SDA->GPIO2, SCL->GPIO3, VCC->5V, GND->GND")
        print("  3. Run: sudo i2cdetect -y 1")
        return False

def test_buzzer(pin=17):
    """Test buzzer"""
    print("\n" + "="*50)
    print(f"TESTING BUZZER on GPIO pin {pin}")
    print("="*50)
    
    try:
        import RPi.GPIO as GPIO
        
        print("\n[1/4] Initializing GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)
        
        print("[2/4] Testing 3 short beeps...")
        for i in range(3):
            print(f"  Beep {i+1}...")
            GPIO.output(pin, True)
            time.sleep(0.2)
            GPIO.output(pin, False)
            time.sleep(0.3)
        
        print("[3/4] Testing 1 long beep...")
        GPIO.output(pin, True)
        time.sleep(1.0)
        GPIO.output(pin, False)
        
        print("[4/4] Cleaning up GPIO...")
        GPIO.cleanup()
        
        print("\n✓ Buzzer test PASSED!")
        print("Did you hear the beeps? (Y/n): ", end='')
        
        return True
        
    except ImportError:
        print("\n✗ RPi.GPIO not installed!")
        print("Install with: sudo apt install python3-rpi.gpio")
        return False
    except Exception as e:
        print(f"\n✗ Buzzer test FAILED: {e}")
        print("\nTroubleshooting:")
        print(f"  1. Check buzzer wiring: + to GPIO{pin}, - to GND")
        print("  2. Make sure it's an ACTIVE buzzer (not passive)")
        print("  3. Try different GPIO pin")
        return False

def main():
    """Run all hardware tests"""
    print("="*50)
    print("ATTENDANCE SYSTEM - HARDWARE TEST")
    print("="*50)
    print("\nThis will test LCD and Buzzer hardware")
    print("Make sure hardware is connected before continuing\n")
    
    # Test I2C first
    i2c_address = test_i2c()
    if i2c_address is None:
        i2c_address = 0x27  # Default
    
    # Test LCD
    lcd_ok = test_lcd(i2c_address)
    
    # Test Buzzer
    buzzer_ok = test_buzzer(17)
    
    # Summary
    print("\n" + "="*50)
    print("HARDWARE TEST SUMMARY")
    print("="*50)
    print(f"I2C Bus:  {'✓ OK' if i2c_address else '✗ FAILED'}")
    print(f"LCD:      {'✓ OK' if lcd_ok else '✗ FAILED'}")
    print(f"Buzzer:   {'✓ OK' if buzzer_ok else '✗ FAILED'}")
    print("="*50)
    
    if lcd_ok and buzzer_ok:
        print("\n✓ All hardware tests PASSED!")
        print("You can now run: python3 main_attendance.py")
        return 0
    else:
        print("\n✗ Some hardware tests FAILED")
        print("Fix the issues above before running main program")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Relay Pin Discovery Script
Tests common GPIO pin combinations to find which ones control your relays
"""

import RPi.GPIO as GPIO
import time

# Common 2-channel relay board GPIO configurations
COMMON_CONFIGS = {
    'Config A': [4, 17],   # Pi HAT common
    'Config B': [18, 19],  # Alternative common
    'Config C': [20, 21],  # Another alternative
    'Config D': [2, 3],    # I2C pins (less common for relays)
    'Config E': [5, 6],    # Alternative pins
    'Config F': [12, 16],  # PWM pins
    'Config G': [13, 26],  # Mixed pins
    'Config H': [22, 27],  # GPIO expansion
}

def setup_gpio():
    """Setup GPIO mode"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

def test_pin_config(name, pins):
    """Test a specific pin configuration"""
    print(f"\n🔍 Testing {name}: GPIO {pins}")
    print("👀 Watch your relay board for clicking/LED activity")
    
    try:
        # Setup pins as outputs
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Start OFF (active LOW)
        
        # Test each pin individually
        for i, pin in enumerate(pins):
            print(f"  📍 Testing GPIO {pin} (should be RELAY {i+1})...")
            
            # Turn relay ON (active LOW)
            GPIO.output(pin, GPIO.LOW)
            print(f"    🟢 GPIO {pin} LOW (relay should click ON)")
            time.sleep(2)
            
            # Turn relay OFF
            GPIO.output(pin, GPIO.HIGH)
            print(f"    ⭕ GPIO {pin} HIGH (relay should click OFF)")
            time.sleep(1)
        
        # Test both together
        print(f"  📍 Testing both relays together...")
        for pin in pins:
            GPIO.output(pin, GPIO.LOW)
        print(f"    🟢 Both ON")
        time.sleep(2)
        
        for pin in pins:
            GPIO.output(pin, GPIO.HIGH)
        print(f"    ⭕ Both OFF")
        time.sleep(1)
        
        # Ask user if this configuration worked
        response = input(f"  ❓ Did you see/hear BOTH relays clicking for {name}? (y/n): ").lower()
        return response.startswith('y')
        
    except Exception as e:
        print(f"    ❌ Error testing {name}: {e}")
        return False
    
    finally:
        # Clean up this configuration
        try:
            for pin in pins:
                GPIO.output(pin, GPIO.HIGH)  # Ensure OFF
        except:
            pass

def main():
    """Main discovery process"""
    print("🕵️ Relay Pin Discovery Tool")
    print("=" * 40)
    print("This script will test common GPIO pin configurations")
    print("to find which ones control your 2-channel relay board.")
    print("\n👀 Watch your relay board for:")
    print("   - Clicking sounds")
    print("   - LED indicators changing")
    print("   - Physical relay switches moving")
    print("\nPress Enter to start...")
    input()
    
    setup_gpio()
    working_config = None
    
    try:
        for name, pins in COMMON_CONFIGS.items():
            if test_pin_config(name, pins):
                working_config = (name, pins)
                print(f"\n🎉 Found working configuration: {name} - GPIO {pins}")
                break
        
        if working_config:
            name, pins = working_config
            print(f"\n✅ SUCCESS! Your relay board uses:")
            print(f"   📌 RELAY 1: GPIO {pins[0]}")
            print(f"   📌 RELAY 2: GPIO {pins[1]}")
            print(f"\n📝 Update your scripts to use these pins:")
            print(f"   RELAY_1_PIN = {pins[0]}")
            print(f"   RELAY_2_PIN = {pins[1]}")
        else:
            print("\n❌ No working configuration found.")
            print("Your relay board might use uncommon pins.")
            print("Check your relay board documentation or try individual pin testing.")
            print("\n🔧 Try these individual pins manually:")
            print("Common relay pins: 4, 17, 18, 19, 20, 21, 22, 27")
        
    except KeyboardInterrupt:
        print("\n⚠️ Discovery interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
    
    finally:
        GPIO.cleanup()
        print("\n🧹 GPIO cleanup completed")

if __name__ == "__main__":
    main()
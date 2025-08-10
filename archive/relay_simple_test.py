#!/usr/bin/env python3
"""
Simple Relay Test - Manual version for Pi Zero 2
Copy this file to your Pi and run it directly
"""

import RPi.GPIO as GPIO
import time

# Common relay HAT configurations - modify if needed
RELAY_PINS = [4, 17, 27, 22]  # Pi Hut 4-Channel Relay HAT (most common)
# Alternative configurations:
# RELAY_PINS = [12, 16, 20, 21]  # Generic 4-channel
# RELAY_PINS = [26, 20, 21]      # 3-channel Waveshare

def setup():
    """Initialize GPIO"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in RELAY_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Start with relays OFF (active LOW)
    
    print(f"GPIO initialized for {len(RELAY_PINS)} relays on pins: {RELAY_PINS}")

def relay_on(index):
    """Turn relay on (0-based index)"""
    GPIO.output(RELAY_PINS[index], GPIO.LOW)
    print(f"Relay {index + 1} ON")

def relay_off(index):
    """Turn relay off (0-based index)"""
    GPIO.output(RELAY_PINS[index], GPIO.HIGH)
    print(f"Relay {index + 1} OFF")

def all_off():
    """Turn all relays off"""
    for i in range(len(RELAY_PINS)):
        relay_off(i)
    print("All relays OFF")

def test_relays():
    """Simple relay test"""
    print("Starting relay self-test...")
    
    # Test each relay individually
    print("\n=== Individual Relay Test ===")
    for i in range(len(RELAY_PINS)):
        print(f"Testing relay {i + 1}")
        relay_on(i)
        time.sleep(2)
        relay_off(i)
        time.sleep(0.5)
    
    # Test all relays together
    print("\n=== All Relays Test ===")
    for cycle in range(3):
        print(f"Cycle {cycle + 1}: All ON")
        for i in range(len(RELAY_PINS)):
            relay_on(i)
        time.sleep(2)
        
        print(f"Cycle {cycle + 1}: All OFF")
        all_off()
        time.sleep(1)
    
    print("\n=== Test Complete ===")

def cleanup():
    """Clean up GPIO"""
    all_off()
    GPIO.cleanup()
    print("GPIO cleanup done")

if __name__ == "__main__":
    try:
        setup()
        test_relays()
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()
#!/usr/bin/env python3
"""
Simple 2-Channel Relay Test - Slower timing for easy observation
Tests 2 relays one at a time with clear delays
"""

import RPi.GPIO as GPIO
import time

# GPIO pins for 2-channel relay board
RELAY_1_PIN = 4   # GPIO 4
RELAY_2_PIN = 17  # GPIO 17

def setup_relays():
    """Initialize GPIO pins for relay control"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup relay pins as outputs
    GPIO.setup(RELAY_1_PIN, GPIO.OUT)
    GPIO.setup(RELAY_2_PIN, GPIO.OUT)
    
    # Start with both relays OFF (HIGH = OFF for active-low relays)
    GPIO.output(RELAY_1_PIN, GPIO.HIGH)
    GPIO.output(RELAY_2_PIN, GPIO.HIGH)
    
    print("✅ GPIO setup complete - both relays OFF")

def relay_on(pin, name):
    """Turn on a relay (active LOW)"""
    GPIO.output(pin, GPIO.LOW)
    print(f"🟢 {name} ON")

def relay_off(pin, name):
    """Turn off a relay (active LOW)"""
    GPIO.output(pin, GPIO.HIGH)
    print(f"⭕ {name} OFF")

def test_relays():
    """Test both relays with slow, observable timing"""
    print("🚀 Starting 2-channel relay test with slow timing...")
    print("👀 Watch the relay LEDs and listen for clicking sounds")
    print()
    
    try:
        # Test each relay individually
        for cycle in range(3):
            print(f"🔄 Cycle {cycle + 1} of 3")
            
            # Test Relay 1
            print("📍 Testing Relay 1...")
            relay_on(RELAY_1_PIN, "RELAY 1")
            time.sleep(3.0)  # 3 seconds ON
            relay_off(RELAY_1_PIN, "RELAY 1")
            time.sleep(2.0)  # 2 seconds OFF
            
            # Test Relay 2
            print("📍 Testing Relay 2...")
            relay_on(RELAY_2_PIN, "RELAY 2")
            time.sleep(3.0)  # 3 seconds ON
            relay_off(RELAY_2_PIN, "RELAY 2")
            time.sleep(2.0)  # 2 seconds OFF
            
            print()
        
        # Test both relays together
        print("🔍 Testing both relays together...")
        relay_on(RELAY_1_PIN, "RELAY 1")
        relay_on(RELAY_2_PIN, "RELAY 2")
        print("🟢 Both relays ON")
        time.sleep(4.0)
        
        relay_off(RELAY_1_PIN, "RELAY 1")
        relay_off(RELAY_2_PIN, "RELAY 2")
        print("⭕ Both relays OFF")
        time.sleep(2.0)
        
        print("🎉 Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Ensure both relays are OFF
        GPIO.output(RELAY_1_PIN, GPIO.HIGH)
        GPIO.output(RELAY_2_PIN, GPIO.HIGH)
        GPIO.cleanup()
        print("🧹 GPIO cleanup completed")

if __name__ == "__main__":
    print("🔧 2-Channel Relay Test")
    print("=" * 30)
    
    setup_relays()
    test_relays()
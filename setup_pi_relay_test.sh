#!/bin/bash
# Setup script for Raspberry Pi Zero 2 Relay Testing
# Run this script directly on your Pi Zero 2

echo "=== Raspberry Pi Zero 2 Relay HAT Setup ==="

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install Python GPIO library if not present
echo "Installing required packages..."
sudo apt install -y python3-rpi.gpio python3-pip

# Create relay test directory
echo "Creating test directory..."
mkdir -p /home/pi/relay_test
cd /home/pi/relay_test

# Create the comprehensive test script
echo "Creating relay test script..."
cat > relay_test.py << 'EOF'
#!/usr/bin/env python3
"""
Raspberry Pi Relay HAT Self-Test Program
Auto-detects common relay HAT configurations and runs comprehensive tests
"""

import RPi.GPIO as GPIO
import time
import sys

class RelayTester:
    def __init__(self):
        self.configs = {
            'pihut_4ch': [4, 17, 27, 22],
            'generic_4ch': [12, 16, 20, 21],
            'waveshare_3ch': [26, 20, 21],
            'generic_8ch': [4, 17, 27, 22, 5, 6, 13, 19]
        }
        self.relay_pins = self.detect_config()
        self.setup_gpio()
    
    def detect_config(self):
        """Try to detect which relay configuration is connected"""
        print("Detecting relay HAT configuration...")
        
        for name, pins in self.configs.items():
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                for pin in pins:
                    GPIO.setup(pin, GPIO.OUT)
                print(f"Detected configuration: {name} - {pins}")
                return pins
            except:
                GPIO.cleanup()
                continue
        
        # Default fallback
        print("Using default 4-channel configuration")
        return self.configs['pihut_4ch']
    
    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # OFF state
    
    def relay_control(self, index, state):
        """Control relay: state True=ON, False=OFF"""
        if 0 <= index < len(self.relay_pins):
            GPIO.output(self.relay_pins[index], GPIO.LOW if state else GPIO.HIGH)
            print(f"Relay {index+1} (GPIO {self.relay_pins[index]}): {'ON' if state else 'OFF'}")
    
    def all_relays(self, state):
        """Control all relays"""
        for i in range(len(self.relay_pins)):
            self.relay_control(i, state)
    
    def test_individual(self):
        """Test each relay individually"""
        print("\n=== Individual Relay Test ===")
        for i in range(len(self.relay_pins)):
            print(f"Testing relay {i+1} of {len(self.relay_pins)}")
            self.relay_control(i, True)
            time.sleep(2)
            self.relay_control(i, False)
            time.sleep(0.5)
    
    def test_sequential(self):
        """Test relays in sequence"""
        print("\n=== Sequential Pattern Test ===")
        for cycle in range(2):
            print(f"Sequential cycle {cycle+1}")
            for i in range(len(self.relay_pins)):
                self.all_relays(False)
                self.relay_control(i, True)
                time.sleep(0.5)
        self.all_relays(False)
    
    def test_all_toggle(self):
        """Test all relays on/off together"""
        print("\n=== All Relays Toggle Test ===")
        for cycle in range(3):
            print(f"All relays cycle {cycle+1}")
            self.all_relays(True)
            time.sleep(1.5)
            self.all_relays(False)
            time.sleep(1)
    
    def run_full_test(self):
        """Run comprehensive test"""
        print(f"Found {len(self.relay_pins)} relays on GPIO pins: {self.relay_pins}")
        print("Starting comprehensive relay test...")
        
        self.all_relays(False)  # Ensure clean start
        time.sleep(1)
        
        self.test_individual()
        time.sleep(2)
        
        self.test_sequential()
        time.sleep(2)
        
        self.test_all_toggle()
        
        self.all_relays(False)  # Clean finish
        print("\n=== TEST COMPLETED SUCCESSFULLY ===")
    
    def cleanup(self):
        self.all_relays(False)
        GPIO.cleanup()
        print("GPIO cleanup completed")

def main():
    tester = None
    try:
        tester = RelayTester()
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if tester:
            tester.cleanup()

if __name__ == "__main__":
    main()
EOF

# Make script executable
chmod +x relay_test.py

echo ""
echo "=== Setup Complete! ==="
echo "To run the relay test:"
echo "  cd /home/pi/relay_test"
echo "  sudo python3 relay_test.py"
echo ""
echo "The test will:"
echo "1. Auto-detect your relay HAT configuration"
echo "2. Test each relay individually"
echo "3. Run sequential pattern tests"
echo "4. Test all relays together"
echo ""
echo "Press Ctrl+C to stop the test at any time."
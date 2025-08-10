#!/usr/bin/env python3
"""
2-Channel Raspberry Pi Relay HAT Self-Test Program
Tests 2 relays with slower timing for easy observation
"""

import RPi.GPIO as GPIO
import time
import sys
import logging
from typing import List

class RelayTester:
    def __init__(self, relay_pins: List[int] = None):
        """
        Initialize relay tester with GPIO pins
        
        Args:
            relay_pins: List of GPIO pins connected to relays
                       If None, uses default 2-channel configuration
        """
        # Default 2-channel configuration
        if relay_pins:
            self.relay_pins = relay_pins
        else:
            self.relay_pins = [4, 17]  # Default 2-channel pins
        
        self.setup_logging()
        self.setup_gpio()
    
    def setup_logging(self):
        """Setup logging for test results"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/relay-admin/relay_test.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_gpio(self):
        """Initialize GPIO pins for relay control"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for pin in self.relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Relays are typically active LOW
        
        self.logger.info(f"GPIO initialized for pins: {self.relay_pins}")
    
    def relay_on(self, relay_index: int):
        """Turn on a specific relay (0-based index)"""
        if 0 <= relay_index < len(self.relay_pins):
            pin = self.relay_pins[relay_index]
            GPIO.output(pin, GPIO.LOW)  # Active LOW
            self.logger.info(f"✅ Relay {relay_index + 1} (GPIO {pin}) ON")
        else:
            self.logger.error(f"❌ Invalid relay index: {relay_index}")
    
    def relay_off(self, relay_index: int):
        """Turn off a specific relay (0-based index)"""
        if 0 <= relay_index < len(self.relay_pins):
            pin = self.relay_pins[relay_index]
            GPIO.output(pin, GPIO.HIGH)  # Active LOW
            self.logger.info(f"⭕ Relay {relay_index + 1} (GPIO {pin}) OFF")
        else:
            self.logger.error(f"❌ Invalid relay index: {relay_index}")
    
    def all_relays_off(self):
        """Turn off all relays"""
        for i in range(len(self.relay_pins)):
            self.relay_off(i)
        self.logger.info("🔴 All relays OFF")
    
    def all_relays_on(self):
        """Turn on all relays"""
        for i in range(len(self.relay_pins)):
            self.relay_on(i)
        self.logger.info("🟢 All relays ON")
    
    def test_individual_relays(self, test_duration: float = 3.0):
        """
        Test each relay individually with slow timing
        
        Args:
            test_duration: How long to keep each relay on (seconds)
        """
        self.logger.info(f"🔍 Starting individual relay test (duration: {test_duration}s per relay)")
        
        for i in range(len(self.relay_pins)):
            self.logger.info(f"📍 Testing relay {i + 1} of {len(self.relay_pins)}")
            
            # Turn on this relay
            self.relay_on(i)
            time.sleep(test_duration)
            
            # Turn off this relay
            self.relay_off(i)
            time.sleep(1.5)  # Longer pause between tests
        
        self.logger.info("✅ Individual relay test completed")
    
    def test_sequential_pattern(self, cycles: int = 2, delay: float = 2.0):
        """
        Test relays in sequential pattern with slow timing
        
        Args:
            cycles: Number of complete cycles
            delay: Delay between relay switches
        """
        self.logger.info(f"🔄 Starting sequential pattern test ({cycles} cycles, {delay}s delay)")
        
        for cycle in range(cycles):
            self.logger.info(f"🔄 Sequential cycle {cycle + 1} of {cycles}")
            
            # Forward sequence
            for i in range(len(self.relay_pins)):
                self.all_relays_off()
                time.sleep(0.5)
                self.relay_on(i)
                time.sleep(delay)
            
            # Brief pause between forward and reverse
            self.all_relays_off()
            time.sleep(1.0)
        
        self.all_relays_off()
        self.logger.info("✅ Sequential pattern test completed")
    
    def test_all_on_off(self, cycles: int = 3, delay: float = 2.0):
        """
        Test all relays on/off simultaneously with slow timing
        
        Args:
            cycles: Number of on/off cycles
            delay: Delay between on/off states
        """
        self.logger.info(f"🔄 Starting all-relays on/off test ({cycles} cycles, {delay}s delay)")
        
        for cycle in range(cycles):
            self.logger.info(f"🔄 All-relays cycle {cycle + 1} of {cycles}")
            
            # All on
            self.all_relays_on()
            time.sleep(delay)
            
            # All off
            self.all_relays_off()
            time.sleep(delay)
        
        self.logger.info("✅ All-relays on/off test completed")
    
    def run_comprehensive_test(self):
        """Run a comprehensive self-test of all 2 relays with slow timing"""
        self.logger.info("🚀 === STARTING 2-CHANNEL RELAY SELF-TEST ===")
        self.logger.info(f"🔌 Detected {len(self.relay_pins)} relays on GPIO pins: {self.relay_pins}")
        
        try:
            # Ensure all relays start in OFF state
            self.all_relays_off()
            time.sleep(2)
            
            # Test 1: Individual relay test (slow)
            self.logger.info("🔍 Test 1: Individual Relay Test")
            self.test_individual_relays(test_duration=3.0)
            time.sleep(3)
            
            # Test 2: Sequential pattern (slow)
            self.logger.info("🔍 Test 2: Sequential Pattern Test")
            self.test_sequential_pattern(cycles=2, delay=2.0)
            time.sleep(3)
            
            # Test 3: All relays on/off (slow)
            self.logger.info("🔍 Test 3: All Relays On/Off Test")
            self.test_all_on_off(cycles=3, delay=2.0)
            time.sleep(2)
            
            # Final state: all off
            self.all_relays_off()
            
            self.logger.info("🎉 === 2-CHANNEL RELAY SELF-TEST COMPLETED SUCCESSFULLY ===")
            
        except Exception as e:
            self.logger.error(f"❌ Error during self-test: {e}")
            self.all_relays_off()  # Ensure safe state
            raise
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.all_relays_off()
        GPIO.cleanup()
        self.logger.info("🧹 GPIO cleanup completed")

def main():
    """Main function to run the 2-channel relay self-test"""
    tester = None
    
    try:
        # Check for command line arguments for custom pin configuration
        if len(sys.argv) > 1:
            # Parse GPIO pins from command line
            pins = [int(pin) for pin in sys.argv[1:]]
            print(f"🔧 Using custom GPIO pins: {pins}")
            tester = RelayTester(relay_pins=pins)
        else:
            # Use default 2-channel configuration
            print("🔧 Using default 2-channel configuration (GPIO 4, 17)")
            tester = RelayTester()
        
        # Run the comprehensive test
        tester.run_comprehensive_test()
        
        print("\n🎉 2-Channel relay self-test completed!")
        print("📋 Check /home/relay-admin/relay_test.log for detailed results.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if tester:
            tester.cleanup()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Consolidated Raspberry Pi Relay Controller
All-in-one script with multiple modes:
- Pin discovery (find which GPIO pins control your relays)
- Simple test (slow, easy to observe relay testing)
- Self-test (comprehensive relay testing)
- GPIO trigger monitor (continuous monitoring of trigger pins)
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Tuple

# =============================================================================
# GLOBAL CONFIGURATION - UPDATE THESE PINS AFTER DISCOVERY
# =============================================================================

# Relay control pins - UPDATE THESE after running discovery mode
RELAY_1_PIN = 22    # GPIO pin that controls RELAY 1
RELAY_2_PIN = 5     # GPIO pin that controls RELAY 2

# GPIO trigger pins for monitoring mode (Physical Pin references)
TRIGGER_1_PIN = 19  # GPIO 19 (Physical Pin 35) - ground to trigger RELAY 1
TRIGGER_2_PIN = 26  # GPIO 26 (Physical Pin 37) - ground to trigger RELAY 2

# Log file location
LOG_FILE = '/home/relay-admin/relay_controller.log'

# =============================================================================
# RELAY CONTROLLER CLASS
# =============================================================================

class RelayController:
    def __init__(self, relay_pins: List[int] = None):
        """
        Initialize relay controller
        
        Args:
            relay_pins: Override default pins [RELAY1, RELAY2]
        """
        # Use provided pins or global config
        self.relay_pins = relay_pins or [RELAY_1_PIN, RELAY_2_PIN]
        
        # GPIO trigger pins (for trigger mode)
        self.trigger_pins = [TRIGGER_1_PIN, TRIGGER_2_PIN]
        
        # Relay states
        self.relay_states = [False, False]
        
        self.setup_logging()
        self.setup_gpio()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_gpio(self):
        """Initialize GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup relay pins as outputs
        for pin in self.relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # OFF (active LOW)
        
        self.logger.info(f"🔧 GPIO initialized for relay pins: {self.relay_pins}")
    
    def setup_trigger_pins(self):
        """Setup trigger pins for monitoring mode"""
        for pin in self.trigger_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.logger.info(f"🔧 Trigger pins setup: {self.trigger_pins}")
        self.logger.info(f"📌 Physical pins: GPIO {self.trigger_pins[0]} = Pin 35, GPIO {self.trigger_pins[1]} = Pin 37")
    
    def relay_on(self, relay_index: int):
        """Turn on a specific relay (0-based index)"""
        if 0 <= relay_index < len(self.relay_pins):
            pin = self.relay_pins[relay_index]
            GPIO.output(pin, GPIO.LOW)  # Active LOW
            self.relay_states[relay_index] = True
            self.logger.info(f"✅ Relay {relay_index + 1} (GPIO {pin}) ON")
        else:
            self.logger.error(f"❌ Invalid relay index: {relay_index}")
    
    def relay_off(self, relay_index: int):
        """Turn off a specific relay (0-based index)"""
        if 0 <= relay_index < len(self.relay_pins):
            pin = self.relay_pins[relay_index]
            GPIO.output(pin, GPIO.HIGH)  # Active LOW
            self.relay_states[relay_index] = False
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
    
    def toggle_relay(self, relay_index: int):
        """Toggle a relay's state"""
        if self.relay_states[relay_index]:
            self.relay_off(relay_index)
        else:
            self.relay_on(relay_index)
    
    def display_status(self):
        """Display current relay and pin configuration"""
        print("📊 Current Configuration:")
        print(f"   RELAY 1: GPIO {self.relay_pins[0]} ({'ON' if self.relay_states[0] else 'OFF'})")
        print(f"   RELAY 2: GPIO {self.relay_pins[1]} ({'ON' if self.relay_states[1] else 'OFF'})")
        print(f"   Trigger 1: GPIO {self.trigger_pins[0]} (Pin 35)")
        print(f"   Trigger 2: GPIO {self.trigger_pins[1]} (Pin 37)")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.all_relays_off()
        GPIO.cleanup()
        self.logger.info("🧹 GPIO cleanup completed")

# =============================================================================
# PIN DISCOVERY CLASS
# =============================================================================

class PinDiscovery:
    def __init__(self):
        """Initialize pin discovery"""
        # Prime suspect pins (most common for 2-channel relay boards)
        self.prime_suspects = [4, 17, 18, 19, 20, 21, 22, 27]
        
        # Additional pins to test if needed
        self.additional_pins = [2, 3, 5, 6, 12, 13, 16, 26]
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
    
    def test_individual_pin(self, pin: int) -> bool:
        """Test if a single pin controls a relay"""
        print(f"\n🔍 Testing GPIO {pin}")
        print("👀 Watch for relay activity (clicking/LED)")
        
        try:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Start OFF
            
            # Test ON
            print(f"   🟢 GPIO {pin} → LOW (should turn relay ON)")
            GPIO.output(pin, GPIO.LOW)
            time.sleep(2)
            
            # Test OFF  
            print(f"   ⭕ GPIO {pin} → HIGH (should turn relay OFF)")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            
            # Ask user
            response = input(f"   ❓ Did GPIO {pin} control a relay? (y/n): ").lower().strip()
            return response.startswith('y')
            
        except Exception as e:
            print(f"   ❌ Error testing GPIO {pin}: {e}")
            return False
        finally:
            try:
                GPIO.output(pin, GPIO.HIGH)  # Ensure OFF
            except:
                pass
    
    def discover_pins(self) -> List[int]:
        """Discover which pins control relays"""
        print("🕵️ Individual Pin Discovery")
        print("=" * 40)
        print("Testing pins one by one to find your relay controllers.")
        print("This will help identify exactly which pins work.\n")
        
        working_pins = []
        
        print("🎯 Testing prime suspect pins first...")
        for pin in self.prime_suspects:
            if self.test_individual_pin(pin):
                working_pins.append(pin)
                print(f"✅ GPIO {pin} controls a relay!")
                
                if len(working_pins) >= 2:
                    print(f"🎉 Found 2 working pins: {working_pins[:2]}")
                    break
        
        # If we need more pins, test additional ones
        if len(working_pins) < 2:
            print(f"\n🔍 Only found {len(working_pins)} pin(s) so far, testing additional pins...")
            for pin in self.additional_pins:
                if pin not in working_pins:
                    if self.test_individual_pin(pin):
                        working_pins.append(pin)
                        print(f"✅ GPIO {pin} controls a relay!")
                        
                        if len(working_pins) >= 2:
                            print(f"🎉 Found 2 working pins: {working_pins[:2]}")
                            break
        
        GPIO.cleanup()
        return working_pins[:2]  # Return first 2 working pins

# =============================================================================
# MODE FUNCTIONS
# =============================================================================

def run_discovery():
    """Run pin discovery mode"""
    discovery = PinDiscovery()
    working_pins = discovery.discover_pins()
    
    if len(working_pins) >= 2:
        print(f"\n🎉 SUCCESS! Found relay pins:")
        print(f"   📌 RELAY 1: GPIO {working_pins[0]}")
        print(f"   📌 RELAY 2: GPIO {working_pins[1]}")
        print(f"\n💡 To update the global configuration, edit this script and change:")
        print(f"   RELAY_1_PIN = {working_pins[0]}")
        print(f"   RELAY_2_PIN = {working_pins[1]}")
        print(f"\n🔧 Or test immediately with:")
        print(f"   python3 relay_controller.py --pins {working_pins[0]} {working_pins[1]} --simple-test")
        return working_pins
    else:
        print(f"\n⚠️ Only found {len(working_pins)} working pin(s): {working_pins}")
        print("Your relay board might use uncommon pins or have different wiring.")
        return []

def run_simple_test(controller: RelayController):
    """Run simple relay test with slow timing"""
    print("🚀 Simple Relay Test (Slow Timing)")
    print("=" * 40)
    controller.display_status()
    print("👀 Watch relay LEDs and listen for clicking\n")
    
    try:
        # Test each relay individually
        for cycle in range(2):
            print(f"🔄 Cycle {cycle + 1} of 2")
            
            # Test Relay 1
            print("📍 Testing Relay 1...")
            controller.relay_on(0)
            time.sleep(3)
            controller.relay_off(0)
            time.sleep(2)
            
            # Test Relay 2
            print("📍 Testing Relay 2...")
            controller.relay_on(1)
            time.sleep(3)
            controller.relay_off(1)
            time.sleep(2)
        
        # Test both together
        print("🔍 Testing both relays together...")
        controller.all_relays_on()
        time.sleep(4)
        controller.all_relays_off()
        
        print("🎉 Simple test completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        controller.all_relays_off()

def run_self_test(controller: RelayController):
    """Run comprehensive self-test"""
    print("🚀 Comprehensive Self-Test")
    print("=" * 40)
    controller.display_status()
    print()
    
    try:
        controller.all_relays_off()
        time.sleep(1)
        
        # Individual test
        print("🔍 Individual relay test...")
        for i in range(len(controller.relay_pins)):
            print(f"Testing relay {i+1}")
            controller.relay_on(i)
            time.sleep(2)
            controller.relay_off(i)
            time.sleep(1)
        
        # Sequential test
        print("🔍 Sequential pattern test...")
        for cycle in range(2):
            for i in range(len(controller.relay_pins)):
                controller.all_relays_off()
                time.sleep(0.5)
                controller.relay_on(i)
                time.sleep(1.5)
        
        # All on/off test
        print("🔍 All relays on/off test...")
        for cycle in range(3):
            controller.all_relays_on()
            time.sleep(1.5)
            controller.all_relays_off()
            time.sleep(1.5)
        
        print("🎉 Self-test completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        controller.all_relays_off()

def run_trigger_monitor(controller: RelayController):
    """Run GPIO trigger monitoring"""
    print("🚀 GPIO Trigger Monitor")
    print("=" * 40)
    controller.display_status()
    print()
    
    controller.setup_trigger_pins()
    
    def signal_handler(sig, frame):
        print("\n⚠️ Shutting down...")
        controller.cleanup()
        sys.exit(0)
    
    def trigger_callback(channel):
        time.sleep(0.05)  # Debounce
        if GPIO.input(channel) == GPIO.LOW:
            if channel == controller.trigger_pins[0]:
                print(f"🎯 Pin 35 (GPIO {channel}) triggered!")
                controller.toggle_relay(0)
            elif channel == controller.trigger_pins[1]:
                print(f"🎯 Pin 37 (GPIO {channel}) triggered!")
                controller.toggle_relay(1)
    
    # Setup interrupts
    for pin in controller.trigger_pins:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=trigger_callback, bouncetime=200)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔄 Monitoring GPIO triggers (Press Ctrl+C to exit)")
    print("📋 Instructions:")
    print(f"   - Connect Pin 35 (GPIO {controller.trigger_pins[0]}) to ground → Toggle RELAY 1")
    print(f"   - Connect Pin 37 (GPIO {controller.trigger_pins[1]}) to ground → Toggle RELAY 2")
    print("   - Available ground pins: 6, 9, 14, 20, 25, 30, 34, 39\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⚠️ Monitor stopped")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Raspberry Pi Relay Controller')
    parser.add_argument('--pins', nargs=2, type=int, metavar=('RELAY1', 'RELAY2'),
                       help=f'Override GPIO pins for relays (current: {RELAY_1_PIN} {RELAY_2_PIN})')
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--discover', action='store_true',
                           help='Discover which GPIO pins control your relays')
    mode_group.add_argument('--simple-test', action='store_true',
                           help='Run simple relay test (slow timing)')
    mode_group.add_argument('--self-test', action='store_true',
                           help='Run comprehensive self-test')
    mode_group.add_argument('--trigger-monitor', action='store_true',
                           help='Monitor GPIO triggers and control relays')
    mode_group.add_argument('--status', action='store_true',
                           help='Show current pin configuration')
    
    args = parser.parse_args()
    
    # Discovery mode doesn't need a controller
    if args.discover:
        run_discovery()
        return
    
    # Status mode just shows configuration
    if args.status:
        print("📊 Current Global Configuration:")
        print(f"   RELAY 1: GPIO {RELAY_1_PIN}")
        print(f"   RELAY 2: GPIO {RELAY_2_PIN}")
        print(f"   TRIGGER 1: GPIO {TRIGGER_1_PIN} (Pin 35)")
        print(f"   TRIGGER 2: GPIO {TRIGGER_2_PIN} (Pin 37)")
        print(f"   Log file: {LOG_FILE}")
        return
    
    # Create controller with specified or global config pins
    relay_pins = args.pins if args.pins else None  # None uses global config
    controller = RelayController(relay_pins)
    
    try:
        if args.simple_test:
            run_simple_test(controller)
        elif args.self_test:
            run_self_test(controller)
        elif args.trigger_monitor:
            run_trigger_monitor(controller)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        controller.cleanup()

def show_usage():
    """Show usage examples"""
    print("🔧 Relay Controller Usage Examples:")
    print("=" * 50)
    print(f"📊 Current global config: RELAY pins {RELAY_1_PIN}, {RELAY_2_PIN}")
    print()
    print("# Discover which pins control your relays:")
    print("python3 relay_controller.py --discover")
    print()
    print("# Show current configuration:")
    print("python3 relay_controller.py --status")
    print()
    print("# Run simple test with global config pins:")
    print("python3 relay_controller.py --simple-test")
    print()
    print("# Run simple test with custom pins:")
    print("python3 relay_controller.py --pins 18 19 --simple-test")
    print()
    print("# Run comprehensive self-test:")
    print("python3 relay_controller.py --self-test")
    print()
    print("# Monitor GPIO triggers:")
    print("python3 relay_controller.py --trigger-monitor")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_usage()
    else:
        main()
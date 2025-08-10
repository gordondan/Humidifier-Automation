#!/usr/bin/env python3
"""
GPIO Triggered Relay Controller
- RELAY 1 switches when GPIO 19 (Physical Pin 35) is grounded
- RELAY 2 switches when GPIO 26 (Physical Pin 37) is grounded
- Runs continuously monitoring GPIO inputs

Physical Pin Wiring Reference:
- GPIO 19 = Physical Pin 35 (Input - connect to ground to trigger RELAY 1)
- GPIO 26 = Physical Pin 37 (Input - connect to ground to trigger RELAY 2) 
- GPIO 4  = Physical Pin 7  (Output - controls RELAY 1)
- GPIO 17 = Physical Pin 11 (Output - controls RELAY 2)
- Ground  = Physical Pin 6, 9, 14, 20, 25, 30, 34, 39 (any ground pin)
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
from datetime import datetime

# GPIO pin configuration (using BCM GPIO numbers, not physical pin numbers)
TRIGGER_1_PIN = 19  # GPIO 19 (Physical Pin 35) - ground to trigger RELAY 1
TRIGGER_2_PIN = 26  # GPIO 26 (Physical Pin 37) - ground to trigger RELAY 2
RELAY_1_PIN = 4     # GPIO 4 (Physical Pin 7) - controls RELAY 1
RELAY_2_PIN = 17    # GPIO 17 (Physical Pin 11) - controls RELAY 2

# Relay states
relay_1_state = False
relay_2_state = False

def log_message(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_gpio():
    """Initialize GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup trigger pins as inputs with pull-up resistors
    GPIO.setup(TRIGGER_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TRIGGER_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup relay pins as outputs
    GPIO.setup(RELAY_1_PIN, GPIO.OUT)
    GPIO.setup(RELAY_2_PIN, GPIO.OUT)
    
    # Start with both relays OFF (HIGH = OFF for active-low relays)
    GPIO.output(RELAY_1_PIN, GPIO.HIGH)
    GPIO.output(RELAY_2_PIN, GPIO.HIGH)
    
    log_message("✅ GPIO setup complete")
    log_message(f"🔍 Monitoring GPIO {TRIGGER_1_PIN} (Pin 35) for RELAY 1 trigger")
    log_message(f"🔍 Monitoring GPIO {TRIGGER_2_PIN} (Pin 37) for RELAY 2 trigger")
    log_message("📌 Connect Pin 35 or Pin 37 to any ground pin to switch relays")

def toggle_relay_1():
    """Toggle RELAY 1 state"""
    global relay_1_state
    relay_1_state = not relay_1_state
    
    if relay_1_state:
        GPIO.output(RELAY_1_PIN, GPIO.LOW)  # ON (active LOW)
        log_message("🟢 RELAY 1 ON")
    else:
        GPIO.output(RELAY_1_PIN, GPIO.HIGH)  # OFF
        log_message("⭕ RELAY 1 OFF")

def toggle_relay_2():
    """Toggle RELAY 2 state"""
    global relay_2_state
    relay_2_state = not relay_2_state
    
    if relay_2_state:
        GPIO.output(RELAY_2_PIN, GPIO.LOW)  # ON (active LOW)
        log_message("🟢 RELAY 2 ON")
    else:
        GPIO.output(RELAY_2_PIN, GPIO.HIGH)  # OFF
        log_message("⭕ RELAY 2 OFF")

def trigger_1_callback(channel):
    """Callback for GPIO 19 trigger (RELAY 1)"""
    # Debounce: check if pin is still low after short delay
    time.sleep(0.05)  # 50ms debounce
    if GPIO.input(TRIGGER_1_PIN) == GPIO.LOW:
        log_message(f"🎯 GPIO {TRIGGER_1_PIN} triggered (grounded)")
        toggle_relay_1()

def trigger_2_callback(channel):
    """Callback for GPIO 26 trigger (RELAY 2)"""
    # Debounce: check if pin is still low after short delay
    time.sleep(0.05)  # 50ms debounce
    if GPIO.input(TRIGGER_2_PIN) == GPIO.LOW:
        log_message(f"🎯 GPIO {TRIGGER_2_PIN} triggered (grounded)")
        toggle_relay_2()

def setup_interrupts():
    """Setup GPIO interrupt handlers"""
    # Trigger on falling edge (when pin goes from HIGH to LOW)
    GPIO.add_event_detect(TRIGGER_1_PIN, GPIO.FALLING, callback=trigger_1_callback, bouncetime=200)
    GPIO.add_event_detect(TRIGGER_2_PIN, GPIO.FALLING, callback=trigger_2_callback, bouncetime=200)
    
    log_message("⚡ Interrupt handlers configured")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    log_message("⚠️ Interrupt received, shutting down...")
    cleanup_and_exit()

def cleanup_and_exit():
    """Clean up GPIO and exit"""
    # Turn off both relays
    GPIO.output(RELAY_1_PIN, GPIO.HIGH)
    GPIO.output(RELAY_2_PIN, GPIO.HIGH)
    log_message("🔴 Both relays turned OFF")
    
    # Clean up GPIO
    GPIO.cleanup()
    log_message("🧹 GPIO cleanup completed")
    log_message("👋 Goodbye!")
    sys.exit(0)

def display_status():
    """Display current relay status"""
    r1_status = "ON" if relay_1_state else "OFF"
    r2_status = "ON" if relay_2_state else "OFF"
    log_message(f"📊 Status: RELAY 1: {r1_status}, RELAY 2: {r2_status}")

def main():
    """Main program loop"""
    log_message("🚀 GPIO Triggered Relay Controller Starting...")
    log_message("=" * 50)
    
    try:
        # Setup GPIO and interrupts
        setup_gpio()
        setup_interrupts()
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, signal_handler)
        
        log_message("🔄 Monitoring GPIO triggers (Press Ctrl+C to exit)")
        log_message("📋 Wiring Instructions:")
        log_message(f"   - Connect Pin 35 (GPIO {TRIGGER_1_PIN}) to any ground pin to toggle RELAY 1")
        log_message(f"   - Connect Pin 37 (GPIO {TRIGGER_2_PIN}) to any ground pin to toggle RELAY 2")
        log_message("   - Available ground pins: 6, 9, 14, 20, 25, 30, 34, 39")
        log_message("")
        
        # Initial status display
        display_status()
        
        # Main loop - just keep the program running
        while True:
            time.sleep(1)  # Check every second
            
            # Optional: Display status every 30 seconds
            if int(time.time()) % 30 == 0:
                display_status()
    
    except KeyboardInterrupt:
        log_message("⚠️ Keyboard interrupt received")
        cleanup_and_exit()
    
    except Exception as e:
        log_message(f"❌ Error: {e}")
        cleanup_and_exit()

if __name__ == "__main__":
    main()
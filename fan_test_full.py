#!/usr/bin/env python3
import time
import os

PWMCHIP = "/sys/class/pwm/pwmchip0"
PWM = f"{PWMCHIP}/pwm0"

# Desired PWM frequency (Hz)
FREQ = 25000  # 25 kHz

# Compute period in nanoseconds
PERIOD_NS = int(1e9 / FREQ)

def write_file(path, value):
    with open(path, "w") as f:
        f.write(str(value))

def setup_pwm():
    # Export channel 0 if not already
    if not os.path.exists(PWM):
        write_file(f"{PWMCHIP}/export", 0)
        time.sleep(0.1)

    # Disable before configuring
    write_file(f"{PWM}/enable", 0)

    # Set the period
    write_file(f"{PWM}/period", PERIOD_NS)

    # Set 100% duty cycle
    write_file(f"{PWM}/duty_cycle", PERIOD_NS)

    # Enable output
    write_file(f"{PWM}/enable", 1)

try:
    setup_pwm()
    print("PWM initialized on GPIO18 at 100% duty cycle.")
    print("Fan running for 10 seconds...")
    time.sleep(10)

finally:
    print("Turning fan off and disabling PWM.")
    write_file(f"{PWM}/duty_cycle", 0)
    write_file(f"{PWM}/enable", 0)

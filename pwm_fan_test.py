#!/usr/bin/env python3
import time
import os

PWMCHIP = "/sys/class/pwm/pwmchip0"
PWM = f"{PWMCHIP}/pwm0"

# Desired PWM frequency (Hz)
FREQ = 25000  # 25 kHz (good for inaudible fan control)

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

    # Set the period (nanoseconds)
    write_file(f"{PWM}/period", PERIOD_NS)

    # Start with 0% duty
    write_file(f"{PWM}/duty_cycle", 0)

    # Enable output
    write_file(f"{PWM}/enable", 1)

def set_duty(percent):
    if percent < 0 or percent > 100:
        raise ValueError("Duty cycle must be between 0 and 100")
    duty_ns = int(PERIOD_NS * (percent / 100.0))
    write_file(f"{PWM}/duty_cycle", duty_ns)

try:
    setup_pwm()
    print("PWM initialized on GPIO18")
    print("Increasing fan speed...")

    # Ramp from 0% to 100% duty in 10% steps
    for p in range(0, 110, 10):
        print(f"  Duty cycle: {p}%")
        set_duty(p)
        time.sleep(2)

    print("Holding at 100% for 5 seconds...")
    time.sleep(5)

    print("Turning fan off.")
    set_duty(0)

finally:
    print("Disabling PWM.")
    write_file(f"{PWM}/enable", 0)

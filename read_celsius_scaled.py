#!/usr/bin/python3

import time
import smbus

# ----- I2C Settings -----
I2C_ADDR = 0x4F
I2C_BUS = 1
SAMPLE_INTERVAL = 1.0  # seconds

bus = smbus.SMBus(I2C_BUS)

# ----- Calibration Data -----
# Replace these with your measured raw ADC counts
raw_0C = 16.8   # raw counts in ice bath
raw_100C = 494.2 # raw counts in boiling water
actual_0C = 0.0
actual_100C = 100.0

# Compute linear correction
slope = (actual_100C - actual_0C) / (raw_100C - raw_0C)
offset = actual_0C - slope * raw_0C

def read_temp_c():
    """Read raw counts from sensor and apply linear correction to return Celsius."""
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 1, 2)
        raw = (data[0] << 8) | data[1]

        # Apply linear correction
        corrected_c = slope * raw + offset
        return corrected_c, raw
    except Exception as e:
        print(f"Error reading probe: {e}")
        return None, None

def main():
    try:
        while True:
            corrected_c, raw = read_temp_c()
            if corrected_c is not None:
                print(f"Raw: {raw:.2f} counts | Corrected: {corrected_c:.2f} °C")
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()

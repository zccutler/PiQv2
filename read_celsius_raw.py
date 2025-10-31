#!/usr/bin/python3

import time
import smbus

I2C_ADDR = 0x4F
I2C_BUS = 1  # typical on Raspberry Pi
SAMPLE_INTERVAL = 1.0  # seconds between readings

bus = smbus.SMBus(I2C_BUS)

def read_temp_c():
    """Read temperature from the sensor and return Celsius."""
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 1, 2)
        raw = (data[0] << 8) | data[1]
        celsius = raw #/ 5.0  # adjust scaling if needed for your probe
        return celsius
    except Exception as e:
        print(f"Error reading probe: {e}")
        return None

def main():
    try:
        while True:
            temp_c = read_temp_c()
            if temp_c is not None:
                print(f"Temperature: {temp_c:.2f} °C")
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()

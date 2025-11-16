#!/usr/bin/python3
import time
import smbus

# ----- I2C Settings -----
I2C_ADDR = 0x4F
I2C_BUS = 1

bus = smbus.SMBus(I2C_BUS)

def read_raw():
    """Read raw ADC counts from the sensor."""
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 1, 2)
        raw = (data[0] << 8) | data[1]
        return raw
    except Exception as e:
        print(f"Read error: {e}")
        return None

def measure_update_rate(duration=5.0):
    """Measure how often the raw reading actually changes over the duration."""
    start_time = time.perf_counter()
    end_time = start_time + duration

    last_raw = None
    change_times = []

    while time.perf_counter() < end_time:
        raw = read_raw()
        now = time.perf_counter()
        if raw is not None and raw != last_raw:
            if last_raw is not None:
                change_times.append(now - last_change_time)
            last_change_time = now
            last_raw = raw

    if change_times:
        avg_interval = sum(change_times) / len(change_times)
        print(f"Unique reading changes: {len(change_times)}")
        print(f"Average interval between changes: {avg_interval:.3f} s")
        print(f"Approx. effective update rate: {1/avg_interval:.2f} Hz")
    else:
        print("No changes detected — check sensor connection or duration too short.")

if __name__ == "__main__":
    print("Measuring effective update rate for 5 seconds...")
    measure_update_rate(duration=5.0)

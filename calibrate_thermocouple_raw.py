#!/usr/bin/python3

import time
import smbus
import statistics

# ----- User Settings -----
I2C_ADDR = 0x4F        # change to your probe's I2C address
I2C_BUS = 1            # typical on Raspberry Pi
SAMPLES_PER_POINT = 30  # number of raw readings per reference
DISCARD_EXTREMES = 10    # number of high/low readings to discard
SAMPLE_INTERVAL = 0.5   # seconds between samples

bus = smbus.SMBus(I2C_BUS)

# -----------------------------
# Read raw ADC counts from probe
# -----------------------------
def read_raw_counts():
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 1, 2)
        raw_counts = (data[0] << 8) | data[1]
        return raw_counts
    except Exception as e:
        print(f"Error reading raw counts: {e}")
        return None

# -----------------------------
# Sample and average raw counts
# -----------------------------
def sample_average(num_samples=SAMPLES_PER_POINT):
    readings = []
    for _ in range(num_samples):
        val = read_raw_counts()
        if val is not None:
            readings.append(val)
        time.sleep(SAMPLE_INTERVAL)
    
    if len(readings) < DISCARD_EXTREMES*2 + 1:
        print("Not enough valid samples to discard extremes!")
        return sum(readings) / len(readings)
    
    readings.sort()
    trimmed = readings[DISCARD_EXTREMES:-DISCARD_EXTREMES]
    avg = sum(trimmed) / len(trimmed)
    return avg

# -----------------------------
# Main calibration helper
# -----------------------------
def main():
    reference_points_c = [0.0, 100.0]  # example: ice bath and boiling water in Celsius
    calibration_data = []

    for ref_c in reference_points_c:
        input(f"Set probe to {ref_c}°C and press Enter when stable...")
        avg_raw = sample_average()
        print(f"Reference {ref_c}°C -> Average raw counts: {avg_raw:.2f}")
        calibration_data.append((avg_raw, ref_c))

    # Compute simple linear fit
    n = len(calibration_data)
    sum_x = sum(x for x, y in calibration_data)
    sum_y = sum(y for x, y in calibration_data)
    sum_xy = sum(x*y for x, y in calibration_data)
    sum_x2 = sum(x*x for x, y in calibration_data)

    slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
    offset = (sum_y - slope*sum_x) / n

    print("\n--- Linear Correction ---")
    print(f"Corrected Temp (°C) = {slope:.4f} * Raw + {offset:.2f}")

    print("\nCalibration Data Points:")
    for raw, ref in calibration_data:
        print(f"Raw: {raw:.2f} -> Ref: {ref}°C")

if __name__ == "__main__":
    main()

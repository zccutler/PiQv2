#!/usr/bin/python3

import time
import smbus

# ----- User Settings -----
address = 0x4f  # replace with your probe's active I2C address
samples_per_point = 20   # number of readings per reference temperature
discard_extremes = 2     # number of high and low readings to discard
sample_interval = 0.5    # seconds between samples

# ----- SMBus setup -----
bus = smbus.SMBus(1)

# -----------------------------
# Probe reading function
# -----------------------------
def read_probe():
    """
    Read the temperature from the Robogaia probe and return Celsius.
    Uses the previously working scaling logic.
    """
    try:
        data = bus.read_i2c_block_data(address, 1, 2)
        val = (data[0] << 8) + data[1]
        celsius = val / 5.0
        return celsius
    except Exception as e:
        print(f"Error reading probe: {e}")
        return None

def sample_average(num_samples=samples_per_point):
    readings = []
    for _ in range(num_samples):
        try:
            val_c = read_probe()
            if val_c is not None:
                readings.append(val_c)  # keep Celsius directly
        except Exception as e:
            print("Error reading probe:", e)
        time.sleep(sample_interval)
    
    if len(readings) < discard_extremes*2 + 1:
        print("Not enough valid samples to discard extremes!")
        return sum(readings) / len(readings)
    
    # discard extremes
    readings.sort()
    trimmed = readings[discard_extremes:-discard_extremes]
    
    avg = sum(trimmed) / len(trimmed)
    return avg

def compute_linear_fit(data_points):
    """
    Simple linear regression for two variables (Raw -> Reference)
    y = slope * x + offset
    """
    n = len(data_points)
    sum_x = sum(x for x, y in data_points)
    sum_y = sum(y for x, y in data_points)
    sum_xy = sum(x*y for x, y in data_points)
    sum_x2 = sum(x*x for x, y in data_points)

    slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
    offset = (sum_y - slope*sum_x) / n
    return slope, offset

def main():
    print("RoboGaia linear calibration helper")
    reference_points = [0,100]  # example °C reference temperatures
    calibration_data = []
    
    for ref in reference_points:
        input(f"Set bath to {ref}°C and press Enter when stable...")
        avg_raw = sample_average()
        print(f"Reference {ref}°C -> Average raw reading: {avg_raw:.2f}")
        calibration_data.append((avg_raw, ref))
    
    slope, offset = compute_linear_fit(calibration_data)
    print("\n--- Linear Correction ---")
    print(f"Corrected Temp (°C) = {slope:.4f} * Raw + {offset:.2f}")
    
    print("\nCalibration Data Points:")
    for raw, ref in calibration_data:
        print(f"Raw: {raw:.2f} -> Ref: {ref}°C")

if __name__ == "__main__":
    main()

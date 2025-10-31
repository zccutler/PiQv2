#!/usr/bin/env python3
import smbus, time, csv, sys
from datetime import datetime

bus = smbus.SMBus(1)
ADDRS = [0x4C, 0x4F]   # RoboGaia addresses
OUT = "robogaia_test_log.csv"

def read_raw_block(addr):
    try:
        # return two raw bytes (no register)
        raw = bus.read_i2c_block_data(addr, 0, 2)
        return raw
    except Exception as e:
        return None

def bytes_to_signed(val):
    if val & 0x8000:
        return val - (1<<16)
    return val

def compute_from_raw(raw_bytes, interpretation="raw_is_counts"):
    b0, b1 = raw_bytes[0], raw_bytes[1]
    raw16 = (b0 << 8) | b1
    signed = bytes_to_signed(raw16)
    # We'll present a few plausible decodings
    dec = {}
    # Interpretation A: raw unit == 1°C (as we saw earlier sometimes)
    dec['counts'] = signed
    dec['degC_counts'] = float(signed)
    dec['degF_counts'] = dec['degC_counts'] * 9.0/5.0 + 32.0
    # Interpretation B: 1/16 °C per count
    dec['degC_div16'] = signed / 16.0
    dec['degF_div16'] = dec['degC_div16'] * 9.0/5.0 + 32.0
    # Interpretation C: tenths of °C (/10)
    dec['degC_div10'] = signed / 10.0
    dec['degF_div10'] = dec['degC_div10'] * 9.0/5.0 + 32.0
    return dec

def sample_once():
    row = {'time': datetime.now().isoformat()}
    for a in ADDRS:
        raw = read_raw_block(a)
        if raw is None:
            row[f'addr_{a:02x}'] = "ERR"
        else:
            dec = compute_from_raw(raw)
            row[f'addr_{a:02x}_b0'] = f"{raw[0]:02x}"
            row[f'addr_{a:02x}_b1'] = f"{raw[1]:02x}"
            row[f'addr_{a:02x}_counts'] = dec['counts']
            row[f'addr_{a:02x}_C_div16'] = f"{dec['degC_div16']:.3f}"
            row[f'addr_{a:02x}_F_div16'] = f"{dec['degF_div16']:.2f}"
            row[f'addr_{a:02x}_C_counts'] = f"{dec['degC_counts']:.3f}"
            row[f'addr_{a:02x}_F_counts'] = f"{dec['degF_counts']:.2f}"
            row[f'addr_{a:02x}_C_div10'] = f"{dec['degC_div10']:.3f}"
            row[f'addr_{a:02x}_F_div10'] = f"{dec['degF_div10']:.2f}"
    return row

def main(samples=30, interval=2.0):
    print(f"Logging to {OUT}, {samples} samples every {interval}s. Press Ctrl-C to stop.")
    with open(OUT, 'w', newline='') as csvfile:
        fieldnames = None
        writer = None
        for i in range(samples):
            r = sample_once()
            if fieldnames is None:
                fieldnames = list(r.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            writer.writerow(r)
            csvfile.flush()
            print(r)
            time.sleep(interval)

if __name__ == "__main__":
    try:
        n = 60
        t = 2.0
        if len(sys.argv) >= 2:
            n = int(sys.argv[1])
        if len(sys.argv) >= 3:
            t = float(sys.argv[2])
        main(samples=n, interval=t)
    except KeyboardInterrupt:
        print("Stopped.")

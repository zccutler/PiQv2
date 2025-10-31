#!/usr/bin/env python3
# Diagnostic tool: try multiple SMBus read methods + scales on RoboGaia addresses
import smbus2, time, math

ADDRESSES = [0x4c, 0x4d, 0x4f]
CMD_REGS = [0, 1]
SCALES = {
    "per_5": lambda v: v / 5.0,
    "per_10": lambda v: v / 10.0,
    "per_16": lambda v: v / 16.0,
    "per_1": lambda v: float(v)
}
AMBIENT_F = 70.0
AMBIENT_TOL_F = 12.0  # highlight candidates within ±12°F of ambient

bus = smbus2.SMBus(1)

def twos_comp(val, bits=16):
    if val & (1 << (bits - 1)):
        return val - (1 << bits)
    return val

def show_candidate(name, raw, swapped, signed_raw, signed_swapped):
    print(f"  {name}: raw=0x{raw:04x} ({raw}), swapped=0x{swapped:04x} ({swapped}), signed_raw={signed_raw}, signed_swapped={signed_swapped}")
    for sname, sfunc in SCALES.items():
        # unsigned interpretations
        val = sfunc(raw)
        f = val * 9.0/5.0 + 32.0
        mark = "<- AMBIENT?" if abs(f - AMBIENT_F) <= AMBIENT_TOL_F else ""
        print(f"    unsigned {sname}: {val:.3f} °C -> {f:.2f} °F {mark}")
        # swapped unsigned
        val2 = sfunc(swapped)
        f2 = val2 * 9.0/5.0 + 32.0
        mark2 = "<- AMBIENT?" if abs(f2 - AMBIENT_F) <= AMBIENT_TOL_F else ""
        print(f"    unsigned swapped {sname}: {val2:.3f} °C -> {f2:.2f} °F {mark2}")
        # signed interpretations
        sval = sfunc(signed_raw)
        sf = sval * 9.0/5.0 + 32.0
        mark3 = "<- AMBIENT?" if abs(sf - AMBIENT_F) <= AMBIENT_TOL_F else ""
        print(f"    signed {sname}: {sval:.3f} °C -> {sf:.2f} °F {mark3}")
        sval2 = sfunc(signed_swapped)
        sf2 = sval2 * 9.0/5.0 + 32.0
        mark4 = "<- AMBIENT?" if abs(sf2 - AMBIENT_F) <= AMBIENT_TOL_F else ""
        print(f"    signed swapped {sname}: {sval2:.3f} °C -> {sf2:.2f} °F {mark4}")

def try_block(addr, cmd):
    try:
        data = bus.read_i2c_block_data(addr, cmd, 2)
        b0, b1 = data[0], data[1]
        raw = (b0 << 8) | b1
        swapped = (b1 << 8) | b0
        signed_raw = twos_comp(raw)
        signed_swapped = twos_comp(swapped)
        return (b0,b1,raw,swapped,signed_raw,signed_swapped)
    except Exception as e:
        return ("ERR", str(e))

def try_word(addr, cmd):
    try:
        w = bus.read_word_data(addr, cmd)
        # smbus read_word_data returns a 16-bit value in little-endian
        # keep both forms for testing
        raw_le = w
        raw_be = ((w << 8) & 0xFF00) | (w >> 8)
        signed_le = twos_comp(raw_le)
        signed_be = twos_comp(raw_be)
        return ('WORD', raw_le, raw_be, signed_le, signed_be)
    except Exception as e:
        return ("ERR", str(e))

def try_byte(addr, reg):
    try:
        b = bus.read_byte_data(addr, reg)
        return b
    except Exception as e:
        return ("ERR", str(e))

def main():
    print("RoboGaia probe explorer")
    print("Addresses:", [hex(a) for a in ADDRESSES])
    print("-" * 60)
    for addr in ADDRESSES:
        print(f"\n== Address 0x{addr:02x} ==")
        # try block reads with cmd/reg 0 and 1
        for cmd in CMD_REGS:
            res = try_block(addr, cmd)
            if isinstance(res, tuple) and res[0] != "ERR":
                b0,b1,raw,swapped,signed_raw,signed_swapped = res
                print(f"block read cmd={cmd}: b0=0x{b0:02x} b1=0x{b1:02x}")
                show_candidate(f"block cmd={cmd}", raw, swapped, signed_raw, signed_swapped)
            else:
                print(f"block cmd={cmd} error: {res}")
        # try word reads
        for cmd in CMD_REGS:
            res = try_word(addr, cmd)
            if res[0] != "ERR":
                _, raw_le, raw_be, signed_le, signed_be = res
                print(f"word read cmd={cmd}: raw_le=0x{raw_le:04x} raw_be=0x{raw_be:04x} signed_le={signed_le} signed_be={signed_be}")
                show_candidate(f"word cmd={cmd}", raw_le, raw_be, signed_le, signed_be)
            else:
                print(f"word cmd={cmd} error: {res}")
        # try single byte reads
        for reg in CMD_REGS:
            res = try_byte(addr, reg)
            print(f"byte read reg={reg}: {res}")
        print("-" * 60)
    print("Done.")

if __name__ == '__main__':
    main()

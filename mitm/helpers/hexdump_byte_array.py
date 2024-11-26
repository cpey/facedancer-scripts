#!/usr/bin/env python3

# Use example:
# python3 parse_byte_array.py "[37, 8, 255, 65]"
# 25 08 ff 41   %..A

import sys
import binascii

def get_ascii_str(ascii_values):
    ascii_str = ""
    for i in ascii_values:
        ascii_str += i
    return ascii_str

def hexdump(data, stdout=True):
    ascii_values = []
    item_n = 0 
    first_match = True
    output = "" 
    for i in data:
        if not item_n % 8 and not first_match:
            output += f"  {get_ascii_str(ascii_values)}\n"
            item_n = 0
            ascii_values = []
        first_match = False
        output += f"{i:02x} "
        if 0x20 <= i <= 0x7E:
            ascii_value = chr(i)
        else:
            ascii_value = '.'
        ascii_values.append(ascii_value)
        item_n += 1
    output += f"  {get_ascii_str(ascii_values)}\n"
    if stdout:
        print(output)
    return output

if __name__ == "__main__":
    hex_string = sys.argv[1]
    hex_values = [int(i.strip(), 10) for i in hex_string.strip("[]").split(",")]
    hexdump(hex_values)

#!/usr/bin/env python3

import argparse
import importlib
import re
import inspect
import sys

from facedancer          import main
from facedancer.proxy    import USBProxyDevice
from facedancer.filters  import USBProxySetupFilters

def hex_type(value):
    try:
        return int(value, 16)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid hexadecimal value: {value}")

def get_class_name(module_path):
    class_expr = re.compile(r'class\s+(\w+)') 
    with open(module_path, 'r') as file:
        for line in file:
            match = class_expr.match(line.strip())
            if match:
                return match.group(1)

def expects_argument(cls):
    ret = False
    signature = inspect.signature(cls.__init__)
    count = 0
    for name, param in list(signature.parameters.items()):
        if name not in ['self', 'args', 'kwargs']:
            count += 1
    if count >=1:
        ret = True
    return ret

def get_module_package(module_path):
    return args.module.strip('.py').lstrip('./').replace('/', '.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to MiTM USB communication")
    parser.add_argument("-l", "--logfile", required=True, help="Output log file")
    parser.add_argument("-e", "--vendor_id", type=hex_type, required=True, help="Vendor ID in hexadecimal (e.g., 0x1234)")
    parser.add_argument("-p", "--product_id", type=hex_type, required=True, help="Product ID in hexadecimal (e.g., 0x5678)")
    parser.add_argument("-m", "--module", required=True, help="Test module to instanciate")
    args = parser.parse_args()

    # Restrict sys.argv to the script name to prevent downstream processing errors
    sys.argv = sys.argv[:1]

    # Create a USB Proxy Device
    proxy = USBProxyDevice(idVendor=args.vendor_id, idProduct=args.product_id)

    # Filter to forward control transfers between the target host and proxied
    # device
    proxy.add_filter(USBProxySetupFilters(proxy, verbose=0))

    class_name = None
    try:
        class_name = get_class_name(args.module)
    except:
        pass
    if not class_name:
        print(f"Error: class not found in module `{args.module}`")
        exit(1)
    module = importlib.import_module(get_module_package(args.module))
    imported_filter = getattr(module, class_name)
    if expects_argument(imported_filter):
        proxy.add_filter(imported_filter(args.logfile))
    else:
        proxy.add_filter(imported_filter())
    
    main(proxy)

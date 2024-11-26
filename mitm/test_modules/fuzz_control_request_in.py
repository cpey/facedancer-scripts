import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump


attrs = [("number", 16), ("value", 16), ("index", 16), ("length", 8)]

class FuzzControlRequestIn(USBProxyFilter):

    def __init__(self, logfile):
        self.logfile = logfile

    def filter_control_in(self, request, data, stalled):

        att_idx = random.randint(0, 3)
        debug_info = f"> IN: request: {request} -- modifying: {attrs[att_idx][0]}\n"
        new_value = random.randint(0, 2**attrs[att_idx][1] - 1)
        setattr(request, attrs[att_idx][0], new_value)
        debug_info += f"new request: {request}\n data: {data}\n"
        debug_info += f" >>> modified: ({attrs[att_idx][0]}, {new_value:#06x})\n"
        print(debug_info)
        with open(self.logfile, "a") as file:
            file.write(debug_info)

        return request, data, stalled

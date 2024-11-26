import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump


class FuzzControlDataIn(USBProxyFilter):

    def __init__(self, logfile):
        self.logfile = logfile
        
    def filter_control_in(self, request, data, stalled):

        recv_data = f"> IN: request: {request}\n data: {data}"
        print(f"{recv_data}\n")
        if len(data):
            hexdump(list(data))
            new_data = bytearray(data)
            idx = random.randint(0, len(new_data) - 1)
            new_data[idx] = random.randint(0, 255)
            modinfo = f" >>> modified: (idx: {idx}, value: {new_data[idx]:#04x})"
            print(f"{modinfo}\n")
            with open(self.logfile, "a") as file:
                file.write(f"{recv_data} sent: {new_data}\n{modinfo}\n")
            data = new_data 

        return request, data, stalled

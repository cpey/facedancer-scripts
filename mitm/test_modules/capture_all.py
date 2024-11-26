import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump


class CaptureAll(USBProxyFilter):

    def __init__(self, logfile):
        self.logfile = logfile

    def filter_in(self, ep_num, data):
        print(f"> IN: ep: {ep_num}\n data: {data}\n")
        hexdump(list(data))
        with open(self.logfile, "a") as file:
            file.write(f"IN: ep: {ep_num} data: {data}\n")

        return ep_num, data

    def filter_control_in(self, request, data, stalled):

        print(f"> CTRL_IN: request: {request}\n data: {data}\n")
        hexdump(list(data))
        with open(self.logfile, "a") as file:
            file.write(f"CTRL_IN: request: {request} data: {data}\n")

        return request, data, stalled

    def filter_out(self, ep_num, data):
        print(f"> OUT: ep: {ep_num}\n data: {data}\n")
        hexdump(list(data))
        with open(self.logfile, "a") as file:
            file.write(f"OUT: ep: {ep_num} data: {data}\n")

        return ep_num, data

    def filter_control_out(self, request, data):

        print(f"> CTRL_OUT: request: {request}\n data: {data}\n")
        hexdump(list(data))
        with open(self.logfile, "a") as file:
            file.write(f"CTRL_OUT: request: {request} data: {data}\n")

        return request, data
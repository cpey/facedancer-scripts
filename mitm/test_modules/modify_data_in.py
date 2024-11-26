import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump

URL = b'https://XXXX'
NEW_URL = b'https://XXXX'
SERIAL = b'XXXX'
NEW_SERIAL = b'XXXX'


class ModifyDataIn(USBProxyFilter):

    def __init__(self, logfile):
        self.logfile = logfile

    def replace_full_url(self, ep_num, data):
        url = URL
        new_url = NEW_URL
        pos = data.find(url)
        debug_info = f"> IN: ep: {ep_num}; data: {data}"
        if pos >= 0:
            data = data[:pos] + new_url + data[pos + len(new_url):]
            debug_info += f"; new_data: {data}"
        with open(self.logfile, "a") as file:
            debug_info += f"\n"
            file.write(debug_info)
        hex_str = hexdump(data, stdout=False)
        print(debug_info)
        print(hex_str)
        return data

    def replace_serial(self, request, data):
        if type(data) == list:
            return data
        serial = SERIAL
        new_serial = NEW_SERIAL
        pos = data.find(serial)
        debug_info = f"> IN: req: {request}; data: {data}"
        if pos >= 0:
            data = data[:pos] + new_serial + data[pos + len(new_serial):]
            debug_info += f"; new_data: {data}"
        with open(self.logfile, "a") as file:
            debug_info += f"\n"
            file.write(debug_info)
        hex_str = hexdump(data, stdout=False)
        print(debug_info)
        print(hex_str)
        return data

    def filter_in(self, ep_num, data):
        data = self.replace_full_url(ep_num, data)
        return ep_num, data

    def filter_control_in(self, request, data, stalled):
        data = self.replace_serial(request, data)
        return request, data, stalled

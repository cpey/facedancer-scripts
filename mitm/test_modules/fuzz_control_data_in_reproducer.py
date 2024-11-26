import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump

FILENAME = "test_results.out"

values = [(1, 69), (6, 156), (1, 106), (7, 235), 
          (12, 62), (3, 147), (1, 17), (2, 60), 
          (6, 197), (39, 96), (3, 121), (3, 248), 
          (11, 11)]

seq_count = 0

class FuzzControlInRepro(USBProxyFilter):

    def filter_control_in(self, request, data, stalled):
        global seq_count

        if seq_count >= len(values):
            seq_count = 0

        idx = values[seq_count][0]
        value = values[seq_count][1]

        new_data = bytearray(data)
        debug_info = f"IN: ep: {request} data: {data}\n"

        if len(data) > idx:
            debug_info += f" sent: {new_data}\n >>> (idx: {idx}, value: {new_data[idx]})\n"
            print(f"> {debug_info}")
            hexdump(list(new_data))
            new_data[idx] = value
            with open(FILENAME, "a") as file:
                file.write(debug_info)
            data = new_data 
            seq_count += 1
        else:
            print(f"> {debug_info}")

        return request, data, stalled

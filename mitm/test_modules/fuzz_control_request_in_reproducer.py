import random
from facedancer.filters import USBProxyFilter
from helpers.hexdump_byte_array import hexdump

FILENAME = "test_results_repro.out"

attrs = dict([("number", 16), ("value", 16), ("index", 16), ("length", 8)])

seq = [("value", 0xb1b2),
       ("length", 4),
       ("value", 0x439e),
       ("index", 0x0785),
       ("value", 0x0125),
       ("number", -1),
       ("value", 0x24eb),
       ("index", 0xfa2c),
       ("value", 0x3316),
       ("value", 0xf025),
       ("value", 0x6820),
       ("value", 0xfc45)]

seq_num = 0

class FuzzControlInRequestRepro(USBProxyFilter):

    def filter_control_in(self, request, data, stalled):

        global seq_num

        if seq_num >= len(seq):
            seq_num = 0
        att = seq[seq_num][0]
        value = seq[seq_num][1]
        if value == -1:
            value = random.randint(0, 2**attrs[att] - 1)
        debug_info = f">>> {seq_num}: {att} -- {value:#06x}"
        print(debug_info)
        print(data)
        setattr(request, att, value)
        seq_num += 1
        with open(FILENAME, "a") as file:
            file.write(debug_info)

        return request, data, stalled

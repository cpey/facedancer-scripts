import random
from facedancer.filters import USBProxyFilter

class MyFilter(USBProxyFilter):

    def filter_in(self, ep_num, data):

        print(ep_num)
        print(data)

        idx = random.randint(0, len(data) - 1)
        data[idx] = random.randint(0, 255)

        # return the endpoint number and modified data
        return ep_num, data

# pylint: disable=unused-wildcard-import, wildcard-import
#
# This file is part of Facedancer.
#
# Modified by Carles Pey.
# 

from facedancer import *
from facedancer import main
from facedancer.classes.hid.usage      import *
from facedancer.classes.hid.descriptor import *
from facedancer.classes.hid.keyboard   import *

import asyncio
import sys
import pprint
import argparse
import logging
import random
from math import *


# Specifies how many simultaneously keys we want to support.
KEY_ROLLOVER = 8

# Pulsation and movement configurations
PULSATION_INTERVAL = 10
MOVEMENT_INTERVAL = 20
PAUSE_RATIO = MOVEMENT_INTERVAL / 5


@use_inner_classes_automatically
class USBMouseDevice(USBDevice):
    """ Simple USB mouse device. """

    name           : str = "USB mouse device"
    product_string : str = "Non-suspicious Mouse"


    class MouseConfiguration(USBConfiguration):
        """ Primary USB configuration: act as a mouse. """


        class MouseInterface(USBInterface):
            """ Core HID interface for our mouse. """

            name         : str = "USB mouse interface"
            class_number : int = 3


            class MouseEventEndpoint(USBEndpoint):
                number        : int             = 3
                direction     : USBDirection    = USBDirection.IN
                transfer_type : USBTransferType = USBTransferType.INTERRUPT
                interval      : int             = 10


            #
            # Raw descriptors -- TODO: build these from their component parts.
            #


            class USBClassDescriptor(USBClassDescriptor):
                number      : int   =  USBDescriptorTypeNumber.HID
                raw         : bytes =  b'\x09\x21\x10\x01\x00\x01\x22\x34\x00'
                                       #                               ^---^-- report desc. len


            class ReportDescriptor(HIDReportDescriptor):
                # 0x05, 0x01,                    // Usage Page (Generic Desktop)        0
                # 0x09, 0x02,                    // Usage (Mouse)                       2
                # 0xa1, 0x01,                    // Collection (Application)            4
                # 0x09, 0x01,                    //  Usage (Pointer)                    6
                # 0xa1, 0x00,                    //  Collection (Physical)              8
                # 0x05, 0x09,                    //   Usage Page (Button)               10
                # 0x19, 0x01,                    //   Usage Minimum (1)                 12
                # 0x29, 0x03,                    //   Usage Maximum (3)                 14
                # 0x15, 0x00,                    //   Logical Minimum (0)               16
                # 0x25, 0x01,                    //   Logical Maximum (1)               18
                # 0x95, 0x08,                    //   Report Count (8)                  20
                # 0x75, 0x01,                    //   Report Size (1)                   22
                # 0x81, 0x02,                    //   Input (Data,Var,Abs)              24
                # 0x05, 0x01,                    //   Usage Page (Generic Desktop)      26
                # 0x09, 0x30,                    //   Usage (X)                         28
                # 0x09, 0x31,                    //   Usage (Y)                         30
                # 0x09, 0x38,                    //   Usage (Wheel)                     32
                # 0x15, 0x81,                    //   Logical Minimum (-127)            34
                # 0x25, 0x7f,                    //   Logical Maximum (127)             36
                # 0x75, 0x08,                    //   Report Size (8)                   38
                # 0x95, 0x03,                    //   Report Count (3)                  40
                # 0x81, 0x06,                    //   Input (Data,Var,Rel)              42
                # 0xc0,                          //  End Collection                     44
                # 0xc0,                          // End Collection                      45

                fields : tuple = (

                    # Identify ourselves as a keyboard.
                    USAGE_PAGE       (HIDUsagePage.GENERIC_DESKTOP),
                    USAGE            (HIDGenericDesktopUsage.MOUSE),
                    COLLECTION       (HIDCollection.APPLICATION),
                    USAGE            (HIDGenericDesktopUsage.POINTER),
                    COLLECTION       (HIDCollection.PHYSICAL),

                    USAGE_PAGE       (HIDUsagePage.BUTTONS),
                    USAGE_MINIMUM    (1),
                    USAGE_MAXIMUM    (3),
                    LOGICAL_MINIMUM  (0),
                    LOGICAL_MAXIMUM  (1),
                    REPORT_COUNT     (3),
                    REPORT_SIZE      (1),
                    INPUT            (variable=True), # 0x02

                    REPORT_COUNT     (1),
                    REPORT_SIZE      (5),
                    #INPUT            (constant=True, variable=True), # 0x03
                    INPUT            (constant=True), # 0x01

                    USAGE_PAGE       (HIDUsagePage.GENERIC_DESKTOP),
                    USAGE            (0x30), # X
                    USAGE            (0x31), # Y
                    USAGE            (0x38), # Wheel
                    LOGICAL_MINIMUM  (0x81),
                    LOGICAL_MAXIMUM  (0x7f),
                    REPORT_SIZE      (8),
                    REPORT_COUNT     (3),
                    INPUT            (variable=True, relative=True), # 0x06

                    END_COLLECTION   (),
                    END_COLLECTION   (),
                )

                # Alternatively, the raw member can be defined directly as done
                # in the GoodFET project. This requires overwriting the
                # __call__ method from the parent class so that it returns
                # self.raw.

                #def __call__(self, index=0):
                #    """Overwrite the parent's __call__ method to return
                #       self.raw."""
                #    return bytes(self.raw)

                # Ref. https://github.com/travisgoodspeed/goodfet/blob/1750cc1e8588af5470385e52fa098ca7364c2863/client/USBMouse.py#L35
                #raw: bytes = ( b'\x05\x01\x09\x02\xa1\x01\x09\x01\xa1'
                #               #                ^-- usage 2 = mouse
                #               b'\x00\x05\x09\x19\x01\x29\x03\x15\x00\x25\x01'
                #               #     first button --^       ^-- last button
                #               b'\x95\x03\x75\x01\x81\x02\x95\x01\x75\x05\x81\x03'
                #               #        ^-- no. of buttons              ^-- padding
                #               b'\x05\x01\x09\x30\x09\x31\x09\x38\x15\x81\x25\x7f'
                #               #               ^-- X   ^-- Y   ^-- wheel
                #               b'\x75\x08\x95\x03\x81\x06\xc0\xc0' )
                #               #                ^-- no. of axes


            @class_request_handler(number=USBStandardRequests.GET_INTERFACE)
            @to_this_interface
            def handle_get_interface_request(self, request):
                # Silently stall GET_INTERFACE class requests.
                request.stall()


    def __post_init__(self):
        super().__post_init__()
        self.t = 0
        self.move_ctrl = 0
        self.x = 0
        self.y = 0
        self.pulsed = 0

    async def set_initial_coords(self, x, y):
        self.x = x
        self.y = y

    def _move(self, endpoint, x, y):
        button_sel = 1
        self.pulsed = (self.pulsed + 1) % (PULSATION_INTERVAL * 2)
        buttons = (self.pulsed < PULSATION_INTERVAL) and button_sel or 0
        position = [(trunc(x)) % 255, (trunc(y)) % 255, 0]
        data = bytes([buttons, *position])
        endpoint.send(data)

    def _update_pos_rand(self):
        if self.t < 10:
            return
        if not (self.move_ctrl % MOVEMENT_INTERVAL):
            self.x = self.x_store
            self.y = self.y_store
            self.x_store = 0
            self.y_store = 0
            pos = random.randint(1, 255)
            self.x += pos
            self.y += pos
            self.x = (self.x + 50 * sin(self.t)) % 255
            self.y = (self.y + 50 * cos(self.t)) % 255
        elif (self.move_ctrl % MOVEMENT_INTERVAL) < PAUSE_RATIO:
            pass
        else:
            self.x_store = self.x
            self.y_store = self.y
            self.x = 0
            self.y = 0

    def _update_pos(self):
        if self.t > 10:
            self.x = (20 * sin(self.t)) % 255
            self.y = (20 * cos(self.t)) % 255

    def handle_data_requested(self, endpoint: USBEndpoint):
        """ Provide data once per host request. """
        self._update_pos_rand()
        self._move(endpoint, self.x, self.y)
        self.t += 0.1
        self.move_ctrl = (self.move_ctrl + 1) % 255

    async def move(self):
        pass

device = USBMouseDevice()

async def move_mouse():
    logging.info("Beginning mouse moving demo...")

    await device.set_initial_coords(0xFB, 1)
    await device.set_initial_coords(0, 1)

    await asyncio.sleep(2)
    await device.set_initial_coords(0, 0)

    logging.info("Location assigned. Idly handling USB requests.")


if __name__ == "__main__":
    main(device, move_mouse())


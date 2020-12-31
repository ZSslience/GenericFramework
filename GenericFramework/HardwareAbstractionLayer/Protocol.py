__author__ = 'jkmody'

"""
########################################################################################################################
# GHERKIN PRIMITIVE ACTION DESCRIPTION                                                                                 #
#                                                                                                                      #
# Title: Protocol.py                                                                                                   #
# Author: Renjith                                                                                                      #
# Date Created: <11/16/2017>                                                                                           #
#                                                                                                                      #
# Description:                                                                                                         #
#   Protocol.py - has all class design definitions to implement/support any protocol stack                             #
#                                                                                                                      #
# Prerequisites:                                                                                                       #
#  - state: OS                                                                                                         #
#                                                                                                                      #
# Modification History:                                                                                                #
# Name           Date                  Reason                                                                          #
# Renjith      11/16/2017    Added FIRMATA protocol support for KB/Mouse emulation with Teensy board                   #
# Renjith      02/07/2018    Code refactoring to PEP8 standards. Phase #3                                              #
########################################################################################################################
"""

########################################################################################################################
# PYTHON IMPORTS                                                                                                       #
########################################################################################################################
import struct
import time
Success = True
Failure = False
#from lib_gherkin import Success, gk_Log
#from common import #DebugLogger


# FIRMATA protocol definitions
# https://github.com/firmata/protocol/blob/master/README.md
class FirmataProtocol(object):
    """
    Implementation of Firmata Protocol
    """
    START_SYSEX = 0xF0
    END_SYSEX = 0xF7
    eVHIDReport = 0x0a

    def __init__(self):
        self.debug_enabled = False  # For developer debugging

    @classmethod
    def __get_buffer_length(cls, *buf):
        return buf.__len__()

    def __calculate_checksum(self, *buf):
        """
        __calculate_checksum(): This if for error checking if a packet is received correctly in the slave Teensy
        :param buf: The packet to find the checksum
        :return: checksum value
        """
        checksum = 0
        for i in range(0, self.__get_buffer_length(*buf)-1):
            checksum ^= buf[i]

        #DebugLogger.print_log(self, Checksum=checksum)
        return checksum

    def create_hid_report(self, cmd_kbm, *args):
        """
        create_hid_report(): Create an HID report of a single keyboard / mouse operation applicable for FIRMATA protocol
        :param cmd_kbm: Keyboard or Mouse operations. {eg release/press/click)
        :param args: The variable arguments that is required by cmd_kbm command.
        :return: HID report
        """
        #DebugLogger.print_log(self, ArgumentSize=self.__get_buffer_length(*args))

        no_of_args = self.__get_buffer_length(*args)
        if no_of_args == 0:
            buf_size = 3
            buf = buf_size * [0]

            buf[0] = buf_size  # Size
            buf[1] = cmd_kbm
            buf[2] = self.__calculate_checksum(*buf)
            return buf
        if no_of_args == 1:
            #DebugLogger.print_log(self, args1=args[0])
            buf_size = 4
            buf = buf_size * [0]
            buf[0] = buf_size  # Size
            buf[1] = cmd_kbm
            buf[2] = args[0]
            buf[3] = self.__calculate_checksum(*buf)
            return buf

        elif no_of_args == 2:
            #DebugLogger.print_log(self, args1=args[0], args2=args[1])
            buf_size = 5
            buf = buf_size * [0]
            buf[0] = buf_size  # Size
            buf[1] = cmd_kbm
            buf[2] = args[0]
            buf[3] = args[1]
            buf[4] = self.__calculate_checksum(*buf)
            return buf

        elif no_of_args == 3:
            #DebugLogger.print_log(self, args1=args[0], args2=args[1], args3=args[2])
            buf_size = 6
            buf = buf_size * [0]
            buf[0] = buf_size  # Size
            buf[1] = cmd_kbm
            buf[2] = args[0]
            buf[3] = args[1]
            buf[4] = args[2]
            buf[5] = self.__calculate_checksum(*buf)
            return buf
        else:
            str_error = u"Arguments not supported"
            gk_Log.exception(str_error)
            raise Exception(str_error)

    def send_hid_report(self, write, write_delay, *hid_reports):
        """
        send_hid_report(): Send the HID reports to any serial device using a write call back routine.
        :param write: Callback write method to write to a serial
        :param write_delay: delay in seconds between each serial write cycles
        :param hid_reports: [IN] Firmata HID reports for KB or mouse operation.
        :return:
        """
        #DebugLogger.print_log(self, write_delay=write_delay)
        try:
            for report in hid_reports:
                #DebugLogger.print_log(self, Report=report, write_delay=write_delay)
                msg = bytearray([self.START_SYSEX, self.eVHIDReport])  # Firmata protocol packet header

                for i in range(0, len(report)):
                    # Send as 2 bytes
                    #DebugLogger.print_log(self, report_i=report[i])
                    pack = struct.pack('>H', report[i])
                    byte0, byte1 = struct.unpack('>BB', pack)

                    #DebugLogger.print_log(self, Byte0=byte0, Byte1=byte1)

                    msg.append(byte0 & 0x7F)
                    msg.append(byte0 >> 7)
                    msg.append(byte1 & 0x7F)
                    msg.append(byte1 >> 7)
                msg.append(self.END_SYSEX)  # Firmata protocol end of packet

                #DebugLogger.print_log(self, MessageSize=report.__len__(), MessagePacket=msg.split())
                write(msg)
                time.sleep(float(write_delay))
            return Success
        except Exception as ex:
            str_error = u"Exception while sending HID report : " + str(ex)
            #gk_Log.exception(str_error)
            raise Exception(str_error)

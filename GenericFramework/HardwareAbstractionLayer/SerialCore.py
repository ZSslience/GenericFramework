__author__ = 'jkmody'

"""
########################################################################################################################
# GHERKIN PRIMITIVE ACTION DESCRIPTION                                                                                 #
#                                                                                                                      #
# Title: SerialDevicesCore.py                                                                                          #
# Author: Renjith                                                                                                      #
# Date Created: <11/08/2017>                                                                                           #
#                                                                                                                      #
# Description:                                                                                                         #
#   SerialDevicesCore - is the base class for all serial devices/ communication                                        #
#   All Hardware that is serial compatible will inherit from this                                                      #
#                                                                                                                      #
# Prerequisites:                                                                                                       #
#  - state: OS                                                                                                         #
#                                                                                                                      #
# Modification History:                                                                                                #
# Name           Date                  Reason                                                                          #
# Renjith      02/07/2018     Code refactoring to PEP8 standards. Phase #3                                             #
# Bhargavi     04/02/2018     Added the cleanup method useful for exception handling                                   #
########################################################################################################################
"""
########################################################################################################################
# PYTHON IMPORTS                                                                                                       #
########################################################################################################################
#from lib_gherkin import gk_Log
import serial
Success = True
Failure = False

class SerialDevicesCore(object):
    """
        Parent class for all serial devices.
    """

    def __init__(self, port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS, timeout=None, write_timeout=None):
        # Create the serial object
        self.__serial_port = self.__configure(port, baudrate, parity, stopbits, bytesize, timeout, write_timeout)

    def __del__(self):
        self.__close_port(self.__serial_port)

    def __configure(self, port, baudrate, parity, stopbits, bytesize, timeout, write_timeout):
        """
        __configure () - Configure the serial port
        :param port: Device name
        :param baudrate: Baud rate such as 9600 or 115200 etc.
        :param parity: Enable parity checking.
        :param stopbits: Number of stop bits.
        :param bytesize: Number of data bits
        :param timeout: Set a read timeout value.
        :param write_timeout: Set a write timeout value.
        :return: serial port object
        """
        port = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits,
                             bytesize=bytesize, timeout=timeout, write_timeout=write_timeout)

        # close the port if already open
        if port.isOpen():
            self.__close_port(port)
        self.__open_port(port)

        return port

    @classmethod
    def __close_port(cls, port):
        """
        __close_port() - close the serial port
        :return: n/a
        """
        port.close()

    @classmethod
    def __open_port(cls, port):
        """
        __open_port() - open the serial port
        :return: n/a
        """
        port.open()

    # Public interfaces

    def update_read_timeout(self, value):
        """
        update_read_timeout() - update the read timeout
        :param value: timeout value in seconds
        :return: n/a
        """
        self.__serial_port.timeout = value

    def update_write_timeout(self, value):
        """
        update_write_timeout() - update the write timeout
        :param value: timeout value in seconds
        :return: n/a
        """
        self.__serial_port.write_timeout = value

    def write(self, value, write_timeout=None):
        """
        write() -  writes the value to the port
        :param value: value to be written in port
        :param write_timeout: max write timeout
        :return: the length of the bytes written
        """
        try:
            org_write_timeout = self.__serial_port.write_timeout
            if org_write_timeout != write_timeout:
                self.update_write_timeout(write_timeout)

            length = self.__serial_port.write(value)

            if org_write_timeout != write_timeout:
                self.update_write_timeout(org_write_timeout)

            return length

        except serial.SerialException as ex:
            str_error = u"Exception while writing serial port:" + str(ex)
            gk_Log.exception(str_error)
            raise Exception(str_error)

    def read(self, size=1, new_read_timeout=None):
        """
        read() - read the bytes mentioned as size or till the timeout.
        :param size: bytes to read
        :param new_read_timeout: max timeout. CAUTION!! (If timeout is not specified the system will starve till it
                                                        receive the specified bytes. It blocks the serial channel)
        :return: the read bytes
        """
        try:
            org_read_timeout = self.__serial_port.timeout
            if org_read_timeout != new_read_timeout:
                self.update_read_timeout(new_read_timeout)

            read_byte_array = self.__serial_port.read(size)

            if org_read_timeout != new_read_timeout:
                self.update_read_timeout(org_read_timeout)

            return read_byte_array

        except serial.SerialException as ex:
            str_error = u"Exception while reading serial port:" + str(ex)
            gk_Log.exception(str_error)
            raise Exception(str_error)

    def cleanup(self):
        """
        Perform the cleanup operations like closing the port for exception handling
        :return: Closes the port if the port attribute exists else returns None
        """
        if self.__serial_port:
            self.__serial_port.close()

__author__ = 'Deepankar Borgohain'
"""
#
# SoundWave BOX library module
# This module provides basic functions to control SoundWave BOX via Serial Port.
# the command for SoundWave is packaged or un-packaged by SoundWave class.
#
# This module use serial port for communicate with Host, default serial setting is:
# portName = COM101, baudrate = 115200 timeout = 2 writeTimeout = 2
#
"""
import binascii
import time
from serial import SerialException, SerialTimeoutException
from serial import Serial
import lib_constants
import library


class SoundWaveError(BaseException):
    pass


class InputError(BaseException):
    pass


class SoundWaveSerialPort:
    def __init__(self, portName, baudrate=115200, timeout=0, writeTimeout=0):
        self.portName = portName
        self.__serialConfig = {'port': portName,
                               'baudrate': baudrate,
                               'bytesize': 8,
                               'timeout': timeout,
                               'write_timeout': writeTimeout,
                               }
        self._serial = None
        self.open()

    def open(self):
        """
        create serial port object and open the it.
        :exception: DeviceError: WindowsError Access is denied or couldn't device.
        """
        try:
            self._serial = Serial(**self.__serialConfig)
        except SerialException as ex:
            library.write_log(lib_constants.LOG_WARNING, "try to open again")
            self._serial = Serial(**self.__serialConfig)

    def __write(self, data):
        self._serial.reset_output_buffer()
        self._serial.reset_input_buffer()
        length = self._serial.write(binascii.a2b_hex(data))
        return length

    def send(self, data):
        length = 0
        if self._serial is None:
            self.open()
        try:
            library.write_log(lib_constants.LOG_DEBUG, 'serial write:{}'.format(data))
            length = self.__write(data)
            library.write_log(lib_constants.LOG_DEBUG, 'write done:{}'.format(length),
                              "None", "None", "None", "None", "None", "None")
        except SerialTimeoutException as ex:
            library.write_log(lib_constants.LOG_ERROR, 'write done:{}'.format(ex))
            self.close()
            library.write_log(lib_constants.LOG_WARNING, 're-open')
            self.open()
            library.write_log(lib_constants.LOG_WARNING, 're-send {0}'.format(data))
            try:
                length = self.__write(data)
                library.write_log(lib_constants.LOG_DEBUG, 're-write done:{}'.format(length))
            except SerialTimeoutException as ex:
                library.write_log(lib_constants.LOG_ERROR, 'write done:{}'.format(ex))
                return False
        return True if length == len(data)//2 else False

    def receive(self, size=None):
        if self._serial is None:
            self.open()
        try:
            library.write_log(lib_constants.LOG_DEBUG, 'serial try receive:{}'.format(size))
            if size is None:
                data = binascii.b2a_hex(self._serial.read()).decode()
            else:
                data = binascii.b2a_hex(self._serial.read(size)).decode()
            library.write_log(lib_constants.LOG_DEBUG, 'receive done:{}'.format(data))
            return data
        except SerialException as ex:
            library.write_log(lib_constants.LOG_ERROR, 'write done:{}'.format(ex) )
            self.close()
            library.write_log(lib_constants.LOG_WARNING, 're-open')
            self.open()
            return ''

    def close(self):
        """
        close serial port
        """
        if self._serial:
            # self._serial.reset_output_buffer()
            # self._serial.reset_input_buffer()
            self._serial.close()
            self._serial = None


class SoundWave(object):
    """

    """

    __SERIAL_CODE_REBOOT			   = '5503000058'

    __SERIAL_CODE_AC_ON                = '550302015b'
    __SERIAL_CODE_AC_OFF               = '550302025c'

    __SERIAL_CODE_USB_TO_PORTA	       = '550301015a'
    __SERIAL_CODE_USB_TO_PORTB  	   = '550301025b'
    __SERIAL_CODE_USB_TO_OPEN		   = '550301035c'

    __SERIAL_CODE_GET_HARDWARE_VERSION = '55000055'
    __SERIAL_CODE_GET_SOFTWARE_VERSION = '55000156'
    __SERIAL_CODE_GET_CUSTOMER_MESSAGE = '55000358'

    __SERIAL_CODE_PRESS_POWER_BUTTON   = '55070f0d0179'
    __SERIAL_CODE_RELEASE_POWER_BUTTON = '55070f0d0078'
    __SERIAL_CODE_PRESS_SYSID_BUTTON   = '55070f0e017a'
    __SERIAL_CODE_RELEASE_SYSID_BUTTON = '55070f0e0079'
    __SERIAL_CODE_PRESS_RESET_BUTTON   = '55070f0f017b'
    __SERIAL_CODE_RELEASE_RESET_BUTTON = '55070f0f007a'
    __SERIAL_CODE_PRESS_NMI_BUTTON     = '55070f10017c'
    __SERIAL_CODE_RELEASE_NMI_BUTTON   = '55070f10007b'

    __SERIAL_CODE_GET_AD_HW_VERSION    = '55050100000000005b'
    __SERIAL_CODE_GET_AD_SW_VERSION    = '55050101000000005c'
    __SERIAL_CODE_GET_FP_HW_VERSION    = '55050f000000000069'
    __SERIAL_CODE_GET_FP_SW_VERSION    = '55050f01000000006a'

    __SERIAL_CODE_ENABLE_LIVE_DEBUG    = '55000459'
    __SERIAL_CODE_DISABLE_LIVE_DEBUG   = '5500055a'

    # FP two-ways port

    TWO_WAYS_DP_OUT_1                  = 1
    TWO_WAYS_DP_OUT_2                  = 2
    TWO_WAYS_DP_OUT_3                  = 3
    TWO_WAYS_DP_OUT_4                  = 4
    TWO_WAYS_DP_OUT_5                  = 5
    TWO_WAYS_DP_OUT_6                  = 6
    TWO_WAYS_DP_OUT_7                  = 7
    TWO_WAYS_DP_OUT_8                  = 8
    TWO_WAYS_DP_OUT_9                  = 9
    TWO_WAYS_DP_OUT_10                 = 10
    TWO_WAYS_DP_OUT_11                 = 11
    TWO_WAYS_DP_OUT_12                 = 12

    # FP One-way port

    POWER_BUTTON                       = 13
    SYSTEM_ID_BUTTON                   = 14
    RESET_BUTTON                       = 15
    NMI_BUTTON                         = 16

    # FP Input

    FP_IN1                             = 17
    FP_IN2                             = 18
    FP_IN3                             = 19

    # FP cmd
    DP_TO_A                            = 0
    DP_TO_B                            = 1

    SP_OPEN                            = 0
    SP_SHORT                           = 1

    def __init__(self, port=None):
        if port is not None:
            self.__port_name = port
        else:
            self.__port_name = 'COM101'
        self.__log_buf = []
        self.open()
        self.__port = None

    def open(self):
        self.__port = SoundWaveSerialPort(portName=self.__port_name, timeout=2, writeTimeout=2)

    def close(self):
        """
        close serial port
        """
        if self.__port is not None:
            self.__port.close()
            self.__port = None

    def __gen_ad_cmd(self, code_list):
        """
        combine <5(max) AD INPUT codes in one SoundWave command, and return it.

        You can use the code from 1 to 60 number for AD INPUT code, others are not supported.

        :param code_list:    integer AD code, the length should between 1 to 5, code range should between 1 to 60.
        :return:        completed command

        """
        cmd = '550701'
        for each in code_list:
            channel = hex(each)[2:]
            if len(channel) == 1:
                channel = '0' + channel
            cmd += channel
        for i in range(5 - len(code_list)):
            cmd += 'ff'
        cmd += '0000000000'

        d = [cmd[0:2], cmd[2:4], cmd[4:6], cmd[6:8], cmd[8:10], cmd[10:12], cmd[12:14], cmd[14:16], cmd[16:18],
             cmd[18:20], cmd[20:22], cmd[22:24], cmd[24:26]]
        checksum = hex(sum(int(x, 16) for x in d))[-2:]
        cmd += checksum
        return cmd

    def __gen_ctr_fp_cmd(self, channel, ctr_switch):
        """
        generate command for control FP switch.

        :param channel: self.DP_OUT_1 ~ self.DP_OUT_12 two-ways switch;
        :param ctr_switch:  self.DP_TO_A or self.DP_TO_B
        :return: complete command
        """
        cmd = '55070f'
        port = hex(channel)[2:]
        if len(port) == 1:
            port = '0' + port
        port.lower()
        cmd += port

        if ctr_switch:
            cmd += '01'
        else:
            cmd += '00'

        d = [cmd[0:2], cmd[2:4], cmd[4:6], cmd[6:8], cmd[8:10]]
        checksum = hex(sum(int(x, 16) for x in d))[-2:]
        cmd += checksum
        return cmd

    def __gen_fp_state_cmd(self, channel):
        """
        generate command for get FP switch status.

        :param channel:self.DP_OUT_1 ~ self.DP_OUT_12 two-ways switch; self.POWER_BUTTON self.SYSTEM_ID_BUTTON self.RESET_BUTTON self.NMI_BUTTON one-way switch; self.FP_IN1 ~ self.FP_IN3 input
        :return: complete command
        """
        port = hex(channel)[2:]
        if len(port) == 1:
            port = '0' + port
        port.lower()
        cmd = '55080f' + port + '00'
        d = [cmd[0:2], cmd[2:4], cmd[4:6], cmd[6:8], cmd[8:10]]
        checksum = hex(sum(int(x, 16) for x in d))[-2:]
        cmd += checksum
        return cmd

    def __gen_set_user_message_cmd(self, user_msg):
        """
        generate command for get customer message command.

        :param user_msg: customer message, format is string, length should not bigger than 128
        :return: complete command
        """
        cmd = ''
        for i in range(len(user_msg)):
            chrtohex = hex(ord(user_msg[i]))[2:]
            if len(chrtohex) == 1:
                chrtohex = '0' + chrtohex
            cmd += chrtohex
        cmd = '550002' + cmd
        while len(cmd) != 262:
            cmd += 'ff'
        l = []
        for i in range(len(cmd)//2):
            l.append(cmd[(2 * i): (2 * (i + 1))])
        checksum = hex(sum(int(x, 16) for x in l))[-2:]
        cmd += checksum
        return cmd

    def __execute_cmd(self, code, res_len):
        """
        :Execute send command to SoundWave and handle received log message.

        :param code: need send to SoundWave command.
        :return: received response message

        :exception
            SoundWaveError: incorrect length or checksum error for received serial data.
        """
        if self.__port is None:
            self.open()

        self.__log_buf = []

        ret = self.__port.send(code)
        if not ret:
            raise SoundWaveError('command length error: {}'.format(code))

        fw_log = ''
        ret_code = ''
        while True:
            ret_value = self.__port.receive(1)
            if ret_value and '55' != ret_value:
                str_log = chr(int(ret_value, 16))
                fw_log += str_log
                if str_log == '\r':
                    library.write_log(lib_constants.LOG_INFO, 'ControlBox log:{0}'.format(fw_log))
                    self.__log_buf.append(fw_log[:-1])
                    fw_log = ''
            elif ret_value == '55':
                coderet = self.__port.receive(res_len//2-1)
                ret_code = '55' + coderet.lower()
                break
            else:
                library.write_log(lib_constants.LOG_INFO, 'Can not receive response!')
                ret_code = None
                break

        return ret_code

    def __check_response(self, cmd, response, compare_with=None):
        """
        :check SoundWave response message.
        If Specified value is default value(None), will check response length and message header according to command.
        Then check the checksum correct or not.
        if compareWith input parameter is not None, will compare it with returned result first.
        if False, will check response message length and message header according to compareWith, # delete this step
        check the checksum correct or not for locate the incorrect.

        :param cmd: the command had sent to SoundWave.
        :param response: received response message.
        :param compare_with: default is None, you can set it Specified value.
        :return: True

        :exception
            SoundWaveError: SoundWave no response.
        """

        if not response:
            raise SoundWaveError('SoundWave seems has some issue, there is no response from it.')

        if compare_with:
            if compare_with.lower() == response.lower():
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, 'response value error, expect {} but got {}'.\
                                  format(compare_with, response))
                return False
        else:
            compare = cmd.lower()
            length = len(compare)
            header = compare[:6]
            if not len(response) == length:
                library.write_log(lib_constants.LOG_ERROR,'length of the value is not equal {}'.format(length))
                return False

            if not ''.join(response).startswith(header):
                library.write_log(lib_constants.LOG_ERROR, 'response format is incorrect, expect header is {} but {}'.\
                                  format(header, response[:6]))
                return False
                # raise SoundWaveError("Header of response message should be {}, but {}".format(header, code[:6]))

            l = []
            for i in range((length - 2)//2):
                l.append(response[(2 * i): (2 * (i + 1))])
            checksum = hex(sum(int(x, 16) for x in l))[-2:]

            if not checksum == response[(length - 2): length]:

                library.write_log(lib_constants.LOG_ERROR, 'check sum is incorrect,expect {} but got:{}'.\
                                  format(checksum, response[(length - 2): length]))
                return False
            return True

    def reboot(self):
        """
        :Make SoundWave reboot.
        For SoundWave FW version 1.1.1.0, this API only reboot MAIN board;
        For FW version 2.0.0.0 or above, this API can reboot the 3 boards(MAIN board, AD board, FP board).

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_REBOOT, len(self.__SERIAL_CODE_REBOOT))
        time.sleep(lib_constants.FIVE_SECONDS)
        return self.__check_response(self.__SERIAL_CODE_REBOOT, response, self.__SERIAL_CODE_REBOOT)

    def ac_power_on(self):
        """
        :send AC_POWER_ON command to SoundWave.

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_AC_ON, len(self.__SERIAL_CODE_AC_ON))
        time.sleep(lib_constants.FIVE_SECONDS)
        ret_response = self.__check_response(self.__SERIAL_CODE_AC_ON, response, self.__SERIAL_CODE_AC_ON)
        if ret_response:
            return lib_constants.LOG_PASS
        else:
            return lib_constants.LOG_FAIL

    def ac_power_off(self):
        """
        :send AC_POWER_OFF command to SoundWave.

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_AC_OFF, len(self.__SERIAL_CODE_AC_OFF))
        time.sleep(lib_constants.FIVE_SECONDS)
        ret_response = self.__check_response(self.__SERIAL_CODE_AC_OFF, response, self.__SERIAL_CODE_AC_OFF)
        if ret_response:
            return lib_constants.LOG_PASS
        else:
            return lib_constants.LOG_FAIL

    def usb_to_port_a(self):
        """
        :Make USB port c connect to USB Port A, and LED A will bright.

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_USB_TO_PORTA, len(self.__SERIAL_CODE_USB_TO_PORTA))

        return self.__check_response(self.__SERIAL_CODE_USB_TO_PORTA, response, self.__SERIAL_CODE_USB_TO_PORTA)

    def usb_to_port_b(self):
        """
        :Make USB port c connect to USB Port B, LED B will bright.

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_USB_TO_PORTB, len(self.__SERIAL_CODE_USB_TO_PORTB))

        return self.__check_response(self.__SERIAL_CODE_USB_TO_PORTB, response, self.__SERIAL_CODE_USB_TO_PORTB)

    def usb_to_open(self):
        """
        :Make USB port c open. LED A and LED B on SoundWave will be turn off.

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_USB_TO_OPEN, len(self.__SERIAL_CODE_USB_TO_OPEN))

        return self.__check_response(self.__SERIAL_CODE_USB_TO_OPEN, response, self.__SERIAL_CODE_USB_TO_OPEN)

    def press_power_button(self):
        """
        :control FP board SP_OUT_1 to short
        switch on FP board swap to Manual, this API no effect, but you can control the POWER button
        switch on FP board swap to auto, this API can control FP board SP_OUT_1, and the POWER button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_PRESS_POWER_BUTTON, len(self.__SERIAL_CODE_PRESS_POWER_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_PRESS_POWER_BUTTON, response,
                                     self.__SERIAL_CODE_PRESS_POWER_BUTTON)

    def release_power_button(self):
        """
        :control FP board SP_OUT_1 to open
        switch on FP board swap to Manual, this API no effect, but you can control the POWER button
        switch on FP board swap to auto, this API can control FP board SP_OUT_1, and the POWER button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_RELEASE_POWER_BUTTON,
                                      len(self.__SERIAL_CODE_RELEASE_POWER_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_RELEASE_POWER_BUTTON, response,
                                     self.__SERIAL_CODE_RELEASE_POWER_BUTTON)

    def press_system_id_button(self):
        """
        :control FP board SP_OUT_1 to short
        switch on FP board swap to Manual, this API no effect, but you can control the SYSTEM_ID button
        switch on FP board swap to auto, this API can control FP board SP_OUT_2, and the SYSTEM_ID button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_PRESS_SYSID_BUTTON, len(self.__SERIAL_CODE_PRESS_SYSID_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_PRESS_SYSID_BUTTON, response,
                                     self.__SERIAL_CODE_PRESS_SYSID_BUTTON)

    def release_system_id_button(self):
        """
        :control FP board SP_OUT_1 to open
        switch on FP board swap to Manual, this API no effect, but you can control the SYSTEM_ID button
        switch on FP board swap to auto, this API can control FP board SP_OUT_2, and the SYSTEM_ID button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_RELEASE_SYSID_BUTTON,
                                      len(self.__SERIAL_CODE_RELEASE_SYSID_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_RELEASE_SYSID_BUTTON, response,
                                     self.__SERIAL_CODE_RELEASE_SYSID_BUTTON)

    def press_reset_button(self):
        """
        :control FP board SP_OUT_1 to short
        switch on FP board swap to Manual, this API no effect, but you can control the RESET button
        switch on FP board swap to auto, this API can control FP board SP_OUT_3, and the RESET button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_PRESS_RESET_BUTTON, len(self.__SERIAL_CODE_PRESS_RESET_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_PRESS_RESET_BUTTON, response,
                                     self.__SERIAL_CODE_PRESS_RESET_BUTTON)

    def release_reset_button(self):
        """
        :control FP board SP_OUT_1 to open
        switch on FP board swap to Manual, this API no effect, but you can control the RESET button
        switch on FP board swap to auto, this API can control FP board SP_OUT_3, and the RESET button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_RELEASE_RESET_BUTTON,
                                      len(self.__SERIAL_CODE_RELEASE_RESET_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_RELEASE_RESET_BUTTON, response,
                                     self.__SERIAL_CODE_RELEASE_RESET_BUTTON)

    def press_nmi_button(self):
        """
        :control FP board SP_OUT_4 to short
        switch on FP board swap to Manual, this API no effect, but you can control the NMI button
        switch on FP board swap to auto, this API can control FP board SP_OUT_4, and the NMI button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_PRESS_NMI_BUTTON, len(self.__SERIAL_CODE_PRESS_NMI_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_PRESS_NMI_BUTTON, response,
                                     self.__SERIAL_CODE_PRESS_NMI_BUTTON)

    def release_nmi_button(self):
        """
        :control FP board SP_OUT_4 to open.
        switch on FP board swap to Manual, this API no effect, but you can control the NMI button
        switch on FP board swap to auto, this API can control FP board SP_OUT_4, and the NMI button no effect

        :return: True or False

        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_RELEASE_NMI_BUTTON,
                                      len(self.__SERIAL_CODE_RELEASE_NMI_BUTTON))

        return self.__check_response(self.__SERIAL_CODE_RELEASE_NMI_BUTTON, response,
                                     self.__SERIAL_CODE_RELEASE_NMI_BUTTON)

    def get_ad_values(self, code_list):
        """
        combine <5(max) AD INPUT codes in one SoundWave command, and read back their value at one time.
        You should identify which AD INPUT values you want to read back via code_list parameter.

        You can use the code from 1 to 60 number for AD INPUT code, others are not supported.

        :param code_list:    integer AD code, the length should between 1 to 5, code range should between 1 to 60.
        :return:        integer AD value list or empty list

        :exception
            INPUT_ERROR: incorrect length or code for code_list.
            SoundWaveError: SoundWave no response.
        """
        if len(code_list) > 5 or len(code_list) == 0:
            library.write_log(lib_constants.LOG_ERROR,'Input AD channel length wrong:{}'.
                              format(code_list))

            raise InputError('expect length of input AD channel list less than 5, but got:{}'.format(len(code_list)))
        for each in code_list:
            if each == 0 or each > 60:
                library.write_log(lib_constants.LOG_ERROR, 'Input AD channel out of range:{}'.
                                  format(each))
                raise InputError('Input AD channel out of range:{}'.format(each))

        cmd = self.__gen_ad_cmd(code_list)

        response = self.__execute_cmd(cmd, len(cmd))

        if self.__check_response(cmd, response):

            hexadstr = [response[16: 18], response[18: 20], response[20: 22], response[22: 24], response[24: 26]]
            advalues = []
            for x in range(len(code_list)):
                advalues.append(float(int(hexadstr[x], 16)*12)/255)
            return advalues
        else:
            return []

    def ctr_fp_two_ways_switch(self, fp_port, action):
        """
        Control specified TWO WAYS switch on FP board., for two-ways port(DP_OUT_1 ~ DP_OUT_12), switch to A or B

        :param fp_port: internal port name same as flag on cable, self.TWO_WAYS_DP_OUT_1 ~ self.TWO_WAYS_DP_OUT_12
        :param action: self.DP_TO_A or self.DP_TO_B
        :return:        True or False

        :exception
            INPUT_ERROR: incorrect port name.
            SoundWaveError: SoundWave no response.
        """
        if fp_port < self.TWO_WAYS_DP_OUT_1 or fp_port > self.TWO_WAYS_DP_OUT_12:
            library.write_log(lib_constants.LOG_ERROR, 'input FP port number out of range:{}'.format(fp_port))
            raise InputError('Expected in self.DP_OUT_1 ~ self.DP_OUT_12 or self.SP_OUT_1 ~ self.SP_OUT_4, '
                             'but got {}'.format(fp_port))

        if action < 0 or action > 1:
            library.write_log(lib_constants.LOG_ERROR, 'FP switch no this action:{}'.format(action))
            raise InputError('Expected self.DP_TO_A(self.SP_OPEN) or self.DP_TO_A(self.SP_SHORT), '
                             'but got {}'.format(action))

        cmd = self.__gen_ctr_fp_cmd(fp_port, action)

        response = self.__execute_cmd(cmd, len(cmd))

        return self.__check_response(cmd, response, None)

    def get_fp_switch_state(self, fp_port):
        """
        Get specified switch's status on FP board.
        for two-ways channel(DP_OUT_1 ~ DP_OUT_12), for one-way port(POWER_BUTTON, SYSTEM_ID_BUTTON,
        RESET_BUTTON, NMI_BUTTON), for input(FP_IN1 ~ FP_IN3).

        :param fp_port: self.TWO_WAYS_DP_OUT_1 ~ self.TWO_WAYS_DP_OUT_12 or self.POWER_BUTTON,
        self.SYSTEM_ID_BUTTON, self.RESET_BUTTON, self.NMI_BUTTON or self.FP_IN1 ~ self.FP_IN3.
        :return: specified Switch's status as '0*' or None
        :exception
            INPUT_ERROR: incorrect port name.
            SoundWaveError: SoundWave no response.
        """
        if fp_port < self.TWO_WAYS_DP_OUT_1 or fp_port > self.FP_IN3:
            library.write_log(lib_constants.LOG_ERROR, 'FP channel out of range:{}'.format(fp_port))
            raise InputError('Expected in self.DP_OUT_1 ~ self.DP_OUT_12 or self.SP_OUT_1 ~ self.SP_OUT_4 '
                             'or self.FP_IN1 ~ self.FP_IN3 ,but got {}'.format(fp_port))

        cmd = self.__gen_fp_state_cmd(fp_port)

        response = self.__execute_cmd(cmd, len(cmd))

        if self.__check_response(cmd, response):

            if self.TWO_WAYS_DP_OUT_1 <= fp_port <= self.TWO_WAYS_DP_OUT_12:
                if int(response[8: 10]) == self.DP_TO_A:
                    return response[8: 10]
                elif int(response[8: 10]) == self.DP_TO_B:
                    return response[8: 10]

            elif fp_port in [self.POWER_BUTTON, self.SYSTEM_ID_BUTTON, self.RESET_BUTTON, self.NMI_BUTTON]:
                if int(response[8: 10]) == self.SP_OPEN:
                    return response[8: 10]
                elif int(response[8: 10]) == self.SP_SHORT:
                    return response[8: 10]

            elif self.FP_IN1 <= fp_port <= self.FP_IN3:
                if int(response[8: 10]) == 1:
                    return response[8: 10]
                elif int(response[8: 10]) == 0:
                    return response[8: 10]

        else:
            return None

    def get_hw_version(self):
        """
        get SoundWave hardware version.

        :return: SoundWave hardware version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_HARDWARE_VERSION, len('5500000000000055'))
        if self.__check_response('5500000000000055', response):

            hexhwstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            hwversion = ''
            for x in hexhwstr:
                hwversion += x
                hwversion += '.'
            return hwversion[:-1]
        else:
            return ''

    def get_sw_version(self):
        """
        get SoundWave software version.

        :return: SoundWave software version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_SOFTWARE_VERSION, len('5500010000000056'))

        if self.__check_response('5500010000000056', response):

            hexswstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            swversion = ''
            for x in hexswstr:
                swversion += x
                swversion += '.'
            return swversion[:-1]
        else:
            return ''

    def get_user_messasge(self):
        """
        get customer message.

        :return: customer message or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_CUSTOMER_MESSAGE, 264)

        if not response:
            raise SoundWaveError('SoundWave seems has some issue, there is no response from it.')

        if not len(response) == 264:
            library.write_log(lib_constants.LOG_ERROR, 'length of the value is not equal 264!')
            return ''

        if not ''.join(response).startswith('550003'):
            library.write_log(lib_constants.LOG_ERROR, "response format is incorrect, expect header is '550003' but {}"
                              .format(response[:6]))
            return ''

        l = []
        for i in range(131):
            l.append(response[(2 * i): (2 * (i + 1))])
        checksum = hex(sum(int(x, 16) for x in l))[-2:]

        if not checksum == response[262: 264]:
            library.write_log(lib_constants.LOG_ERROR,'check sum is incorrect,expect {} but got:{}'
                              .format(checksum, response[262: 264]))
            return ''

        user_msg = ''
        for i in range(3, 131):
            if l[i] == 'ff':
                break
            str_log = chr(int(l[i], 16))
            user_msg += str_log

        return user_msg

    def set_user_messasge(self, user_msg):
        """
        Set customer message, message length should less than 128.

        :param user_msg: customer message, is a string, length less than 128
        :return: True or False
        :exception
            SoundWaveError: SoundWave no response.
        """

        if user_msg == '':
            library.write_log(lib_constants.LOG_ERROR,'No customer message input!')
            raise SoundWaveError('No customer message input!')

        if len(user_msg) > 128:
            library.write_log(lib_constants.LOG_ERROR, 'length of the value is out of range!')
            raise SoundWaveError('Length of customer message should not bigger than 128, but {}'.format(len(user_msg)))

        cmd = self.__gen_set_user_message_cmd(user_msg)

        response = self.__execute_cmd(cmd, len(cmd))

        return self.__check_response(cmd, response)

    def get_ad_hw_version(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above, get AD board hardware version.

        :return: ad board hardware version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_AD_HW_VERSION, len(self.__SERIAL_CODE_GET_AD_HW_VERSION))
        if self.__check_response(self.__SERIAL_CODE_GET_AD_HW_VERSION, response):

            hexhwstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            adhwversion = ''
            for x in hexhwstr:
                adhwversion += x
                adhwversion += '.'
            return adhwversion[:-1]
        else:
            return ''

    def get_ad_sw_version(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above, get AD board software version.

        :return: ad board software version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_AD_SW_VERSION, len(self.__SERIAL_CODE_GET_AD_SW_VERSION))

        if self.__check_response(self.__SERIAL_CODE_GET_AD_SW_VERSION, response):

            hexswstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            adswversion = ''
            for x in hexswstr:
                adswversion += x
                adswversion += '.'
            return adswversion[:-1]
        else:
            return ''

    def get_fp_hw_version(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above, get FP board hardware version.

        :return: FP board hardware version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_FP_HW_VERSION, len(self.__SERIAL_CODE_GET_FP_HW_VERSION))
        if self.__check_response(self.__SERIAL_CODE_GET_FP_HW_VERSION, response):

            hexhwstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            fphwversion = ''
            for x in hexhwstr:
                fphwversion += x
                fphwversion += '.'
            return fphwversion[:-1]
        else:
            return ''

    def get_fp_sw_version(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above, get FP board software version.

        :return: FP board software version as 'xx.xx.xx.xx' or ''
        :exception
            SoundWaveError: SoundWave no response.
        """

        response = self.__execute_cmd(self.__SERIAL_CODE_GET_FP_SW_VERSION, len(self.__SERIAL_CODE_GET_FP_SW_VERSION))

        if self.__check_response(self.__SERIAL_CODE_GET_FP_SW_VERSION, response):

            hexswstr = [response[-10: -8], response[-8: -6], response[-6: -4], response[-4: -2]]
            fpswversion = ''
            for x in hexswstr:
                fpswversion += x
                fpswversion += '.'
            return fpswversion[:-1]
        else:
            return ''

    def enable_live_debug(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above release edition.
         enable live debug function, can get more log messages for debug.

        :return: True or False
        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_ENABLE_LIVE_DEBUG, len(self.__SERIAL_CODE_ENABLE_LIVE_DEBUG))
        return self.__check_response(self.__SERIAL_CODE_ENABLE_LIVE_DEBUG, response,
                                     self.__SERIAL_CODE_ENABLE_LIVE_DEBUG)

    def disable_live_debug(self):
        """
        New API, only for soundWave software version 2.0.1.0 or above release edition.
        disable live debug function, only get critical message.

        :return: True or False
        :exception
            SoundWaveError: SoundWave no response.
        """
        response = self.__execute_cmd(self.__SERIAL_CODE_DISABLE_LIVE_DEBUG, len(self.__SERIAL_CODE_DISABLE_LIVE_DEBUG))
        return self.__check_response(self.__SERIAL_CODE_DISABLE_LIVE_DEBUG, response,
                                     self.__SERIAL_CODE_DISABLE_LIVE_DEBUG)


def main():
    sdw = SoundWave()
    # print(sdw.ac_power_on())
    print(sdw.ac_power_off())
    # print(sdw.usb_to_port_a())
    # print(sdw.usb_to_port_b())


if __name__ == '__main__':
    main()

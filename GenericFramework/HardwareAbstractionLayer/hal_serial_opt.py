import serial
import os
import time
from SoftwareAbstractionLayer import lib_parse_config
from SoftwareAbstractionLayer import library
from SoftwareAbstractionLayer import lib_constants


class SerialComm:
    def __init__(self):
        """
        Function Name       : __init__()
        Parameters          : None
        Functionality       : Initialize Serial and key event parameters.
        Function Invoked    : serial(pyserial)
        Return Value        : None
        """
        self._SERIAL_CONFIG = {
            'BAUDRATE': 115200,  # 1st read from config
            'PORT': 'COM100',  # 1st read from config
            'PARITY': serial.PARITY_NONE,
            'TIMEOUT': None,
            'BUFFER_SIZE': 128000000
        }

        self._CTRL_KEY_MAP = {}
        self._FN_KEY_MAP = {}

        self._CLIENT_CTRL_KEY_MAP = {
            # Client CTRL_KEY_MAP with PCANSI Protocol
            'ENTER': b'\r',
            'ESC': b'\x1b',
            'DLE': b'\x10',
            'PAGE_UP': b'\x1b[I',
            'PAGE_DOWN': b'\x1b[G',
            'HOME': b'\x1b[H',
            'END': b'\x1b[F',
            'DELETE': b'\x1b[X',
            'INSERT': b'\x1b[@',
            'SPACE': b'\x20',  # SP
            'BACKSPACE': b'\x08',  # Common Usage
            'CTRL_ALT_DELETE': b'\x1bR\x1br\x1bR',  # Common Usage
            # Not Defined'CTRL': b'',
            # Not Defined'ALT': b'',
            # Not Defined'SHIFT': b'',
            'PLUS': b'\x10+',  # Common Usage
            'MINUS': b'\x10-'  # Common Usage
        }

        self._CLIENT_FN_KEY_MAP = {
            # Client FN_KEY_MAP with PCANSI Protocol
            'F1': b'\x1b[M',
            'F2': b'\x1b[N',
            'F3': b'\x1b[O',
            'F4': b'\x1b[P',
            'F5': b'\x1b[Q',
            'F6': b'\x1b[R',
            'F7': b'\x1b[S',
            'F8': b'\x1b[T',
            'F9': b'\x1b[U',
            'F10': b'\x1b[V',
            'F11': b'\x1b[W',
            'F12': b'\x1b[X',
        }

        self._SERVER_CTRL_KEY_MAP = {
            # Server CTRL_KEY_MAP with VT100 Protocol
            'ENTER': b'\r',
            'ESC': b'\x1b',  # ^[ \e
            'DLE': b'\x10',  # ^P
            'PAGE_UP': b'\x1b[?',
            'PAGE_DOWN': b'\x1b[/',
            'HOME': b'\x1b[H',
            'END': b'\x1b[K',
            'DELETE': b'\x1b[P',
            'INSERT': b'\x1b[@',
            'SPACE': b'\x20',  # SP
            'BACKSPACE': b'\x08',  # ^H \b
            'CTRL_ALT_DELETE': b'\x1bR\x1br\x1bR',  # Common Usage
            # Not Defined'CTRL': b' ',
            # Not Defined'ALT': b' ',
            # Not Defined'SHIFT': b' ',
            'PLUS': b'\x10+',  # Common Usage
            'MINUS': b'\x10-'  # Common Usage
        }

        self._SERVER_FN_KEY_MAP = {
            # Server FN_KEY_MAP with VT100 Protocol
            'F1': b'\x1bOP',
            'F2': b'\x1bOQ',
            'F3': b'\x1bOR',
            'F4': b'\x1bOS',
            'F5': b'\x1bOT ',
            'F6': b'\x1bOU',
            'F7': b'\x1bOV',
            'F8': b'\x1bOW',
            'F9': b'\x1bOX',
            'F10': b'\x1bOY',
            'F11': b'\x1bOZ',
            'F12': b'\x1bO[',
        }

        self._SERVER_VT100_PLUS_CTRL_KEY_MAP = {
            # Server CTRL_KEY_MAP with VT100 PLUS Protocol
            'ENTER': b'\r',
            'ESC': b'\x1b',  # ^[ \e
            'DLE': b'\x10',  # ^P
            'PAGE_UP': b'\x1b?',
            'PAGE_DOWN': b'\x1b/',
            'HOME': b'\x1bh',
            'END': b'\x1bk',
            'DELETE': b'\x1b-',
            'INSERT': b'\x1b+',
            'SPACE': b'\x20',  # SP
            'BACKSPACE': b'\x08',  # ^H \b
            'CTRL_ALT_DELETE': b'\x1bR\x1br\x1bR',  # Common Usage
            # Not Defined'CTRL': b' ',
            # Not Defined'ALT': b' ',
            # Not Defined'SHIFT': b' ',
            'PLUS': b'\x10+',  # Common Usage
            'MINUS': b'\x10-'  # Common Usage
        }

        self._SERVER_VT100_PLUS_FN_KEY_MAP = {
            # Server FN_KEY_MAP with VT100 PLUS Protocol
            'F1': b'\x1b1',
            'F2': b'\x1b2',
            'F3': b'\x1b3',
            'F4': b'\x1b4',
            'F5': b'\x1b5 ',
            'F6': b'\x1b6',
            'F7': b'\x1b7',
            'F8': b'\x1b8',
            'F9': b'\x1b9',
            'F10': b'\x1b0',
            'F11': b'\x1b!',
            'F12': b'\x1b@',
        }

        # Platform specific key map enumeration
        try:
            SUT_CONFIG = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)), os.path.pardir,
                r"SoftwareAbstractionLayer\system_configuration.ini")
            config = lib_parse_config.ParseConfig()
            read_sut_type = config.get_value(
                SUT_CONFIG, 'SUT_Config', 'SUT_TYPE')
            read_baudrate = int(config.get_value(
                SUT_CONFIG, 'Serial', 'BAUDRATE'))
            read_port = str(config.get_value(
                SUT_CONFIG, 'Serial', 'PORT'))
            self._SERIAL_CONFIG['BAUDRATE'] = read_baudrate
            self._SERIAL_CONFIG['PORT'] = read_port
            if read_sut_type == 'client':
                self._CTRL_KEY_MAP = self._CLIENT_CTRL_KEY_MAP
                self._FN_KEY_MAP = self._CLIENT_FN_KEY_MAP
            elif read_sut_type == 'server':
                read_server_terminal_type = config.get_value(
                    SUT_CONFIG, 'SUT_Config', 'SERVER_TERM_TYPE')
                if read_server_terminal_type == 'VT100':
                    self._CTRL_KEY_MAP = self._SERVER_CTRL_KEY_MAP
                    self._FN_KEY_MAP = self._SERVER_FN_KEY_MAP
                elif read_server_terminal_type == 'VT100_PLUS' \
                        or read_server_terminal_type == 'VTUTF8':
                    self._CTRL_KEY_MAP = self._SERVER_VT100_PLUS_CTRL_KEY_MAP
                    self._FN_KEY_MAP = self._SERVER_VT100_PLUS_FN_KEY_MAP
            else:
                raise AssertionError('SUT_Config value invalid.')
        except Exception as e:
            raise Exception('Serial Configuration Failed: ' + e)

        # Initialize Serial Port
        self.ser_imp = serial.Serial()
        self.ser_imp.baudrate = self._SERIAL_CONFIG['BAUDRATE']
        self.ser_imp.port = self._SERIAL_CONFIG['PORT']
        self.ser_imp.parity = self._SERIAL_CONFIG['PARITY']
        self.ser_imp.timeout = self._SERIAL_CONFIG['TIMEOUT']
        # Common key map configuration
        self._NAVI_KEY_MAP = {
            'UP': b'\x1b[A',
            'DOWN': b'\x1b[B',
            'RIGHT': b'\x1b[C',
            'LEFT': b'\x1b[D',
        }
        self._SPEC_KEY_MAP = {
            'SOH': b'\x01',  # ^A
            'STX': b'\x02',  # ^B
            'ETX': b'\x03',  # ^C
            'EOT': b'\x04',  # ^D
            'ENQ': b'\x05',  # ^E
            'ACK': b'\x06',  # ^F
            'BEL': b'\x07',  # ^G \a
            'HT': b'\x09',  # ^I \t
            'LF': b'\x0a',  # ^J \n
            'VT': b'\x0b',  # ^K \v
            'FF': b'\x0c',  # ^L \f
            'CR': b'\x0d',  # ^M \r
            'SO': b'\x0e',  # ^N
            'SI': b'\x0f',  # ^O
            'DLE': b'\x10',  # ^P
            'DC1': b'\x11',  # ^Q
            'DC2': b'\x12',  # ^R
            'DC3': b'\x13',  # ^S
            'DC4': b'\x14',  # ^T
            'NAK': b'\x15',  # ^U
            'SYN': b'\x16',  # ^V
            'ETB': b'\x17',  # ^W
            'CAN': b'\x18',  # ^X
            'EM': b'\x19',  # ^Y
            'SUB': b'\x1a',  # ^Z
            'FS': b'\x1c',  # ^\
            'GS': b'\x1d',  # ^]
            'RS': b'\x1e',  # ^^
            'US': b'\x1f',  # ^_
        }

    def serial_io_hii_enum(self, key_type, key_event, key_step=1,
                           time_out=1, leave_closed=True):
        """
        Function Name       : serial_io_hii_enum()
        Parameters          :
                key_type    : 0 - navi / 1 - ctrl / 2 - func / 3 - istr
                key_event   : navi - UP/DOWN/RIGHT/LEFT
                              ctrl - ESC/ENTER/DELETE/INSERT
                              func - F1/F2/F3/F4/F5/F6/F7/F8/F9/F10/F11/F12
                              istr - one or mor string to be input
                key_step    : duplicate key steps for same key event input
                time_out    : int - operate timeout for getting buffer
                leave_closed: bool - True as default to close port after write
        Functionality       : A serial enum to get input key event sent
                              with buffer lines in list output.
        Function Invoked    : SerialComm._imp_port_mngr()
                              SerialComm._imp_buffer_sync()
        Return Value        : [byte_buffer_1, byte_buffer_2, ...]
        """

        def _imp_navi_key(self, navi_event, n_step=1, key_timeout=1):
            temp_buffer = []
            if navi_event in self._NAVI_KEY_MAP:
                for i in range(n_step):  # pylint: disable=unused-variable
                    self._imp_port_buf_cls()
                    self.ser_imp.write(self._NAVI_KEY_MAP[navi_event])
                    time.sleep(key_timeout)
                    navi_buf = self._imp_buffer_sync()
                    temp_buffer.append(navi_buf)
                return temp_buffer
            else:
                raise ValueError(
                    'Parameter Error: ' + navi_event + ' not found')

        def _imp_ctrl_key(self, ctrl_event, c_step=1, key_timeout=1):
            temp_buffer = []
            if ctrl_event in self._CTRL_KEY_MAP:
                for i in range(c_step):  # pylint: disable=unused-variable
                    self._imp_port_buf_cls()
                    self.ser_imp.write(self._CTRL_KEY_MAP[ctrl_event])
                    time.sleep(key_timeout)
                    ctrl_buf = self._imp_buffer_sync()
                    temp_buffer.append(ctrl_buf)
                return temp_buffer
            else:
                raise ValueError(
                    'Parameter Error: ' + ctrl_event + ' is not found')

        def _imp_func_key(self, func_event, f_step=1, key_timeout=1):
            temp_buffer = []
            if func_event in self._FN_KEY_MAP:
                for i in range(f_step):  # pylint: disable=unused-variable
                    self._imp_port_buf_cls()
                    self.ser_imp.write(self._FN_KEY_MAP[func_event])
                    time.sleep(key_timeout)
                    func_buf = self._imp_buffer_sync()
                    # print(type(func_buf))
                    temp_buffer.append(func_buf)
                return temp_buffer
            else:
                raise ValueError(
                    'Parameter Error: ' + func_event + ' is not found')

        def _imp_text_str(self, istr_event, i_step=1, key_timeout=1):
            temp_buffer = []
            for i in range(i_step):  # pylint: disable=unused-variable
                self._imp_port_buf_cls()
                is_string = (type(istr_event) == str)
                if is_string:
                    if len(istr_event) < 17:
                        input_string = istr_event.encode()
                        self.ser_imp.write(input_string)
                    else:
                        for alp in istr_event:
                            input_string = alp.encode()
                            self.ser_imp.write(input_string)
                            time.sleep(0.05)
                    time.sleep(key_timeout)
                    istr_buf = self._imp_buffer_sync()
                else:
                    raise ValueError(
                        'Parameter Error: ' + istr_event + ' is not string')
                # print(type(istr_buf))
                temp_buffer.append(istr_buf)
            return temp_buffer

        def _imp_spec_key(self, spec_event, s_step=1, key_timeout=1):
            temp_buffer = []
            if spec_event in self._SPEC_KEY_MAP:
                for _ in range(s_step):  # pylint: disable=unused-variable
                    self._imp_port_buf_cls()
                    self.ser_imp.write(self._SPEC_KEY_MAP[spec_event])
                    time.sleep(key_timeout)
                    spec_buf = self._imp_buffer_sync()
                    # print(type(func_buf))
                    temp_buffer.append(spec_buf)
                return temp_buffer
            else:
                raise ValueError(
                    'Parameter Error: ' + spec_event + ' is not found')

        _key_event_map = {
            0: _imp_navi_key,
            1: _imp_ctrl_key,
            2: _imp_func_key,
            3: _imp_text_str,
            4: _imp_spec_key
        }

        key_buffer = []
        self._imp_port_mngr('open')
        if key_type in _key_event_map:
            self._log_write('DEBUG', 'KeyType: ' + str(key_type)
                              + ' Value: ' + str(key_event) + ' Steps: '
                              + str(key_step))
            key_buffer = _key_event_map[key_type](self, key_event, key_step,
                                                  time_out)
            if leave_closed:
                self._imp_port_mngr('close')
            return key_buffer
        else:
            raise ValueError(
                'Parameter Error: ' + key_type + ' is not found')

    def serial_adv_enum(self, key_bytes, time_out=1, leave_closed=True):
        """
        Function Name       : serial_adv_enum()
        Parameters          :
                key_bytes   : list - input operatabe serial bytes
                              i.e: ['exit', '\r']
                time_out    : int - operate timeout for getting buffer
                leave_closed: bool - True as default to close port after write

        Functionality       : Use confirmed bytes to operate serial port.
        Function Invoked    : SerialComm._imp_port_mngr()
                              SerialComm._imp_buffer_sync()
        Return Value        : [byte_buffer]
        """
        key_buffer = []
        if type(key_bytes) == list:
            self._imp_port_mngr('open')
            for key_serial in key_bytes:
                self._imp_port_buf_cls()
                self.ser_imp.write(key_serial.encode())
                time.sleep(time_out)
                enum_buf = self._imp_buffer_sync()
                key_buffer.append(enum_buf)
            self._log_write('DEBUG', 'KeyType: ' + str(type(key_bytes))
                              + ' Value: ' + str(key_bytes))
            if leave_closed:
                self._imp_port_mngr('close')
        else:
            raise ValueError(
                'Parameter Error: ' + key_bytes + ' is not valid')
        return key_buffer

    def serial_plain_cmd(self, command='', time_out=1, leave_closed=True):
        """
        Function Name       : serial_plain_cmd()
        Parameters          :
                command     : str - command as string as input
                              i.e: ls
                time_out    : int - operate timeout for getting buffer
                leave_closed: bool - True as default to close port after write
        Functionality       : Support command line with \r as execute input.
                              Extended 10 times buffer size control.
        Function Invoked    : SerialComm._imp_port_mngr()
                              SerialComm._imp_buffer_sync()
        Return Value        : [byte_buffer]
        """
        key_buffer = []
        if type(command) == str:
            self._imp_port_mngr('open')
            self.ser_imp.set_buffer_size(
                    rx_size=self._SERIAL_CONFIG['BUFFER_SIZE'],
                    tx_size=self._SERIAL_CONFIG['BUFFER_SIZE'])
            for alp in command:
                input_string = alp.encode()
                self.ser_imp.write(input_string)
                time.sleep(0.01)
            self.ser_imp.write(b'\r')
            time.sleep(time_out)
            cmd_buf = self._imp_buffer_sync()
            key_buffer.append(cmd_buf)
            self._log_write('DEBUG', 'Command Value: ' + str(command))
            if leave_closed:
                self._imp_port_mngr('close')
        else:
            raise ValueError(
                'Parameter Error: ' + command + ' is not string')
        return key_buffer

    def serial_io_get_buffer(self, time_out=1):
        """
        Function Name       : serial_io_get_buffer()
        Parameters          : time_out: int - operate timeout for getting
                              buffer
        Functionality       : Get current screen buffer.
        Pre-Condition       : SerialComm._imp_port_mngr('open')
        Function Invoked    : SerialComm._imp_buffer_sync()
        Return Value        : [byte_buffer]
        """
        key_buffer = []
        time.sleep(time_out)
        sio_buf = self._imp_buffer_sync()
        key_buffer.append(sio_buf)
        return key_buffer

    def _imp_port_mngr(self, state):
        """
        Function Name       : _imp_port_mngr()
        Parameters          : state: str - open, close as serial control
        Functionality       : Serial port control with state
        Pre-Condition       : class imported as object
        Function Invoked    : serial[Pyserial]
        Return Value        : bool: 0 - success, 1 - failed
        """
        if state == 'open':
            if not self.ser_imp.is_open:
                self.ser_imp.open()
                self.ser_imp.set_buffer_size(
                    rx_size=self._SERIAL_CONFIG['BUFFER_SIZE'],
                    tx_size=self._SERIAL_CONFIG['BUFFER_SIZE'])
                return True
            else:
                self._log_write('WARNING', 'Serial port already opened')
                return True
        elif state == 'close':
            if self.ser_imp.is_open:
                self.ser_imp.close()
                return True
            else:
                return True
        else:
            raise KeyError(
                'Parameter Error: ' + state + ' is not valid')

    def _log_write(self, result, info):
        TEST_CASE_ID = "hal_serial_opt"
        SCRIPT_ID = "hal_serial_opt.py"
        if result == "INFO":
            library.write_log(lib_constants.LOG_INFO, 'Status: %s' % (info),
                              TEST_CASE_ID, SCRIPT_ID)
            return True
        elif result == "DEBUG":
            library.write_log(lib_constants.LOG_INFO, 'Debug: %s' % (info),
                              TEST_CASE_ID, SCRIPT_ID)
            return True
        elif result == "WARNING":
            library.write_log(lib_constants.LOG_WARNING, 'Warning: %s' % (info),
                              TEST_CASE_ID, SCRIPT_ID)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, 'Error: %s' % (info),
                              TEST_CASE_ID, SCRIPT_ID)
            return False

    def _imp_buffer_sync(self):
        if self.ser_imp.is_open:
            self._log_write('DEBUG', 'Buffer InWaiting: ' +
                              str(self.ser_imp.in_waiting))
            data = self.ser_imp.read(self.ser_imp.in_waiting)
            return data
        else:
            raise AssertionError(
                'Operate Error: Serial Port is not opened')

    def _imp_port_buf_cls(self):
        if self.ser_imp.is_open:
            self.ser_imp.flushInput()
            self.ser_imp.flushOutput()
        else:
            raise AssertionError(
                'Operate Error: Serial Port is not opened')

    def _imp_print_data(self, in_buffer):
        self._log_write('DEBUG', 'Buffer type is: ' + str(type(in_buffer))
                          + ' Buffer length is: ' + str(len(in_buffer)))
        print(*in_buffer, sep="\n")

    def __del__(self):
        if self.ser_imp.is_open:
            self.ser_imp.close()


if __name__ == "__main__":
    ser_test = SerialComm()
    step_1 = ser_test.serial_adv_enum(['\x1bR\x1br\x1bR'], 5)
    step_2 = ser_test.serial_io_hii_enum(2, 'F2', 1)
    step_3 = ser_test.serial_io_hii_enum(0, 'DOWN', 6, 0.5)
    step_4 = ser_test.serial_io_hii_enum(1, 'ENTER', 2, 1, False)
    step_5 = ser_test.serial_plain_cmd('help', 5)
    ser_test.serial_io_hii_enum(3, 'This is a long hello world from aliens.')
    step_4 = ser_test.serial_io_hii_enum(1, 'ENTER')
    step_6 = ser_test.serial_io_hii_enum(3, 'exit')
    step_7 = ser_test.serial_io_hii_enum(1, 'ENTER')
    # ser_test._imp_print_data(step_5)

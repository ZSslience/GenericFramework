import os
import sys
import datetime
import logging
from SoftwareAbstractionLayer import lib_parse_config


class WriteLog:
    def __init__(self, test_case_id=None):
        """
        Function Name       : __init__()
        Parameters          : str: test_case_id is mandatory for case
                                   optional for mw/*al debugging.
        Functionality       : Initialize logging events.
        Function Invoked    : os, sys, logging
        Return Value        : None
        """
        # Read logging level from system_configuration.ini
        SUT_CONFIG = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), os.path.pardir,
            r"SoftwareAbstractionLayer\system_configuration.ini")
        config = lib_parse_config.ParseConfig()
        stream_log_level = config.get_value(
            SUT_CONFIG, 'Logging', 'LEVEL')

        # Mapped log level agaisnt logging module
        _log_level_match = {
            'DEBUG':    logging.DEBUG,
            'INFO':     logging.INFO,
            'WARNING':  logging.WARNING,
            'ERROR':    logging.ERROR
        }

        self.tc_id = test_case_id
        if self.tc_id:
            self.logger = logging.getLogger(self.tc_id)
        else:
            self.logger = logging.getLogger('DEBUG')
        self.logger.setLevel(logging.DEBUG)

        # Logging format consolidated from designs.
        FULL_FORMAT = '%(asctime)s %(name)s %(filename)s %(lineno)d \
%(funcName)s %(module)s %(levelname)-5s %(message)s'
        PRINT_FORMAT = '%(asctime)s %(levelname)-8s %(message)-s'

        pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
        log_dir = pwd + r"\log"
        if not (os.path.exists(log_dir)):
            os.mkdir(log_dir)
        print_format = logging.Formatter(PRINT_FORMAT, "%Y-%m-%d %H:%M:%S")
        full_format = logging.Formatter(FULL_FORMAT)
        _date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        # Set TC related log format and handler if have
        if self.tc_id:
            log_file_name = self.tc_id + ".log"
            file_handle = log_dir + "\\" + log_file_name
            self._file_h = logging.FileHandler(file_handle)
            self._file_h.setLevel(logging.DEBUG)
            self._file_h.setFormatter(full_format)
        # Set full run log format and handler
        full_log_file = "run_" + _date_now + ".log"
        full_file_handle = log_dir + "\\" + full_log_file
        self._full_h = logging.FileHandler(full_file_handle)
        self._full_h.setLevel(logging.DEBUG)
        self._full_h.setFormatter(full_format)
        # Set stdio stream format and handler
        self._stream_h = logging.StreamHandler()
        self._stream_h.setLevel(_log_level_match[stream_log_level])
        self._stream_h.setFormatter(print_format)

        self._OUT_LEVEL = {
            'DEBUG':    [0, 'DEBUG: ', self.logger.debug],
            'INFO':     [1, 'INFO: ', self.logger.info],
            'WARNING':  [2, 'WARNING:', self.logger.warning],
            'ERROR':    [3, 'ERROR: ', self.logger.error],
            'PASS':     [4, 'PASS: ', self.logger.info],
            'FAIL':     [5, 'FAIL: ', self.logger.error]
        }

        if self.tc_id:
            self.logger.addHandler(self._file_h)
        self.logger.addHandler(self._stream_h)
        self.logger.addHandler(self._full_h)

    def write_log(self, level, msg,
                  toolname=None, info_fetched=None):
        """
        Function Name       : write_log()
        Parameters          : level - mandatory string with right log levels.
                                DEBUG - logging.DEBUG
                                INFO - logging.INFO
                                WARNING - logging.WARNING
                                ERROR - logging.ERROR
                                PASS - logging.INFO
                                FAIL - logging.ERROR
                              msg - mandatory string with converted messages.
                              toolname - optional string with tools used.
                              info_fetched - optional string with info output.
        Functionality       : Get log output on screen and save in file.
        Pre-Condition       : Log message is ready and level is confirmed.
        Function Invoked    : None
        Return Value        : Bool - 0  # Success
        """

        # for handler in self.logger.handlers:
        #     print(handler)
        # read test script name with the python file called.
        script_id = os.path.basename(sys.argv[0])
        if self.tc_id:
            test_case_id = self.tc_id
            msg_format = 'TC_ID: %12s SCRIPT_NAME: %12s  %12s' \
                % (test_case_id, script_id, msg)
        else:
            msg_format = ' %12s: %12s' % (script_id, msg)
        if toolname:
            msg_format = msg_format + " TOOL_USED: " + toolname + \
                " TOOL_LOG:" + str(info_fetched)
        if level in self._OUT_LEVEL:
            # print(self._OUT_LEVEL[level][0] + log_msg_format)
            self._OUT_LEVEL[level][2](self._OUT_LEVEL[level][1] +
                                      str(msg_format))
        else:
            raise ValueError(
                'Log Level Error: ' + level + ' is not matched')

    def __del__(self):
        if self.tc_id:
            self.logger.removeHandler(self._file_h)
        self.logger.removeHandler(self._stream_h)
        self.logger.removeHandler(self._full_h)


if __name__ == "__main__":
    # pure_log = WriteLog()
    # pure_log.write_log('ERROR', 'Here is a tight log message.')
    rich_log = WriteLog('CSS-IVE-12345678')
    rich_log.write_log("INFO", "CSS-IVE-123456 test Started.")
    rich_log.write_log("DEBUG", "Start booting to BIOS.")
    rich_log.write_log("ERROR", "No boot media found.")
    rich_log.write_log("PASS", "Boot successfully.")
    rich_log.write_log("FAIL", "Boot failed.")

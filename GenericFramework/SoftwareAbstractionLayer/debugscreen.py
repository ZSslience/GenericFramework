import re
import os
from SoftwareAbstractionLayer import lib_parse_config


class Vt100Cmd(object):
    def __init__(self, name, value):
        '''
        Function Name   :__init__()
        Parameters      :name: attribute description
                         value: attribute value
        Functionality   :Initialize Vt100Cmd object
        Return          :None
        '''
        self.name = name
        self.param = value


CFG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             r"serial_keywords.ini")


class DebugScreen(object):
    def __init__(self, cfg_file_path=CFG_FILE_PATH):
        '''
        Function Name   :__init__()
        Parameters      :split_section_title: split chars section name
                         conf_file: config file path
        Functionality   :Initialize config information
        Return Value    :None
        '''
        self.cfg_file = cfg_file_path
        self.cfg_file_info = self._get_cfg_file_info(self.cfg_file)

    def _get_cfg_file_info(self, cfg_file_path):
        try:
            parser = lib_parse_config.ParseConfig()
            sections = parser.parse_config_file(cfg_file_path).sections()
            cfg_file_info = dict()
            for section in sections:
                cfg_file_info[section] = dict()
                cfg_file_info[section][0] = parser.get_value(cfg_file_path, section, 'RegularExpression')
                cfg_file_info[section][1] = parser.get_value(cfg_file_path, section, 'Description')
                cfg_file_info[section][2] = parser.get_value(cfg_file_path, section, 'MarkChar')
                cfg_file_info[section][3] = re.compile(cfg_file_info[section][0])
        except Exception as e:
            raise e
        return cfg_file_info

    def _str_to_int(self, patternchars):
        '''
        Function Name   :_strToint()
        Parameter       :patternchars:the chars without markchars obtained by
                         regular matching
        Functionality   :convert a string to an integer
        Return          :an integer if exist, else raise exception
        '''
        try:
            if patternchars.isdigit():
                return int(patternchars)
            else:
                num = (ord(patternchars[0]) - ord('0')) * 10
                num += int(patternchars[1])
                return num
        except Exception as e:
            raise e

    def _get_segmentword_info(self, markchars, pattern_results):
        '''
        Function Name   :_get_segmentword_info()
        Parameter       :markchars:the attribute name defined by vt100，such as: m,H
                         pattern_results:the chars include the attribute name and
                         value obtained by regular matching
        Functionality   :get the attribute value through markchars
                         example: pattern_results=37m;
                                  markchars='m'
                                  attribute_value=37
        Return          :the attribute value, else raise
        '''
        try:
            parm = list()
            markchars_split = markchars.split(',')
            start_index = 0
            for mark in markchars_split:
                end_index = pattern_results.find(mark)
                parm.append(self._str_to_int(pattern_results[start_index:end_index]))
                start_index = end_index + 1
            parm.append(pattern_results[start_index:])
        except Exception as e:
            raise e
        return parm

    def _get_screen_info(self, serial_output):
        '''
        Function Name   :_get_screen_info()
        Parameter       :serial_output: output string from serial port
        Functionality   :According the serial protocol, the serial output is converted
                        to the 'Vt100Cmd' object.
        Return          :A list of Vt100Cmd objects.
        '''
        screen_info = list()
        try:
            split_chars = b'\x1b['
            serial_splitinfo = serial_output.split(split_chars)
            for segment_words in serial_splitinfo:
                if segment_words != b'':
                    segment_words = segment_words.decode('utf-8', 'ignore')
                    for section in self.cfg_file_info:
                        dec = self.cfg_file_info[section][1]
                        markchars = self.cfg_file_info[section][2]
                        pattern = self.cfg_file_info[section][3]
                        pattern_results = re.match(pattern, segment_words)
                        if pattern_results is not None:
                            segmentword_results = \
                                self._get_segmentword_info(markchars, segment_words)
                            if len(segmentword_results) > 2:
                                param = [segmentword_results[0], segmentword_results[1]]
                                screen_info.append(Vt100Cmd(dec, param))
                                screen_info.append(Vt100Cmd("draw", [segmentword_results[2]]))
                            else:
                                screen_info.append(Vt100Cmd(dec, [segmentword_results[0]]))
                                if segmentword_results[1] != '':
                                    screen_info.append(Vt100Cmd("draw", [segmentword_results[1]]))
        except Exception as e:
            raise e
        return screen_info

    def serial_output_split(self, serial_output):
        '''
        Function Name   :debugscreen_output()
        Parameters      :serial_output: the bytes data output from serial port
        Functionality   :Convert the serial output to 'Vt100Cmd' object that
                         describe the debug information.
        Return          :A list of Vt100Cmd objects.
        '''
        try:
            debug_info = self._get_screen_info(serial_output)
        except Exception as e:
            raise e
        return debug_info


def test():
    '''
    Function Name   :test()
    Parameters      :None
    Functionality   :unitest
    Return          :None
    '''
    debug = DebugScreen()
    serial_output = b'\x1b[0m The SFP Auto\x1b[37medkshell\x1b[40m\x1b[03;:0H                         \x1b[22;27H     ' \
                    b'                     \x1b[23;27H<Enter>=Complete Entry    \x1b[23;03H^v=Move Highlight       ' \
                    b'\x1b[22;03H                        \x1b[22;53H                           \x1b[22;27H            ' \
                    b'              \x1b[23;53HEsc=Exit Entry             \x1b[0m\x1b[37m\x1b[44m\x1b[10;33H          ' \
                    b'     \x1b[11;33H               \x1b[12;33H               \x1b[13;33H               \x1b[' \
                    b'10;33H\x1b[10;33H/-------------\\\x1b[11;33H|\x1b[11;47H|\x1b[12;33H|\x1b[12;47H|\x1b[' \
                    b'11;35HEnabled\x1b[1m\x1b[37m\x1b[46m\x1b[12;35HDisabled\x1b[0m\x1b[37m\x1b[44m\x1b[' \
                    b'13;33H\\-------------/ '
    debug_info = debug.serial_output_split(serial_output)
    for info in debug_info:
        print(info.name + ": " + str(info.param))


if __name__ == '__main__':
    test()

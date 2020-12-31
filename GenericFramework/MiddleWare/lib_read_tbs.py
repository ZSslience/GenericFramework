"""
File Name   : lib_read_tbs.py
Description : run TBSLogGenerator tool and parse log to search event and get its PCR value
Author      : Jinliang
Created On  : 12 Apr 2020
"""
import os
import codecs

from SoftwareAbstractionLayer import utils, library, lib_constants
from MiddleWare.lib_run_command import run_command


def run_tbslog_generator(test_case_id, script_id, log_level="ALL", tbd="None"):
    """run TBSLogGenerator.exe command, and return log file
    :param test_case_id: test case id
    :param script_id: script id
    :param log_level: log level
    :param tbd: tbd
    :return: log file if successfully run command, otherwise False
    """
    tool_name = utils.ReadConfig("TBSLOG_TOOL", "TOOL_NAME")
    if "FAIL:" in tool_name:
        library.write_log(lib_constants.LOG_FAIL, tool_name, test_case_id,
                          script_id, log_level, tbd)
        return False

    log_file = run_command(tool_name, test_case_id, script_id)
    if not log_file:
        library.write_log(lib_constants.LOG_FAIL,
                          "Failed to run command %s" % tool_name,
                          test_case_id, script_id,
                          log_level, tbd)
    return log_file


def verify_event_and_pcr(log_file, event, pcr, test_case_id, script_id, event_index=1, log_level="ALL", tbd="None"):
    """parse log file to verify whether event and response PCR exists, return PCR value or False
    :param log_file: TBS log file
    :param event: event to be verify
    :param pcr: PCR key response to event, e.g. PCR[00], PCR[01]
    :param test_case_id: test case id
    :param script_id: script id
    :param event_index: index of duplicate event in log, starts from 1
    :param log_level: log level
    :param tbd: tbd
    :return: PCR value both response to event and PCR key, otherwise False
    """
    result = False
    pcr_value = ''
    event_idx = int(event_index) - 1
    event_idx = event_idx if event_idx >= 0 else 0

    if not os.path.exists(log_file):
        library.write_log(lib_constants.LOG_WARNING, "Log file %s does not exists" % log_file,
                          test_case_id, script_id, log_level, tbd)
        return result, pcr_value

    with codecs.open(log_file, 'r', encoding='ansi') as fp:
        info = fp.readlines()

    for idx in range(len(info)):
        # verify event in log file
        if event.upper() in info[idx].upper():
            if event_idx > 0:
                event_idx -= 1
                continue

            library.write_log(lib_constants.LOG_INFO,
                              "%s event be present in logs" % event,
                              test_case_id, script_id,
                              log_level, tbd)
            idx += 2
            if idx >= len(info):
                library.write_log(lib_constants.LOG_WARNING,
                                  "%s value under %s event not be present in logs" % (pcr, event),
                                  test_case_id, script_id,
                                  log_level, tbd)
                return result, pcr_value

            if info[idx].upper().startswith(pcr.upper()):
                pcr_value = info[idx].upper().split('=')[1].strip()
                if pcr_value:
                    library.write_log(lib_constants.LOG_INFO,
                                      "%s value under %s event be present in logs" % (pcr, event),
                                      test_case_id, script_id,
                                      log_level, tbd)
                    library.write_log(lib_constants.LOG_INFO,
                                      "%s value = %s" % (pcr, pcr_value),
                                      test_case_id, script_id,
                                      log_level, tbd)
                    result = True
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                                      "%s value under %s event not be present in logs" % (pcr, event),
                                      test_case_id, script_id,
                                      log_level, tbd)
            break
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "The %dth %s event not be present in logs" % (int(event_index), event),
                          test_case_id, script_id,
                          log_level, tbd)

    return result, pcr_value


def get_event_data(log_file, event, test_case_id, script_id, event_index=1, log_level="ALL", tbd="None"):
    """parse log file to search event and return event data
    :param log_file: TBS log file
    :param event: event to be searched
    :param test_case_id: test case id
    :param script_id: script id
    :param event_index: index of duplicate event in log, starts from 1
    :param log_level: log level
    :param tbd: tbd
    :return: True and event data tuple contain raw data (hex) list and ASCII string, as:
             event_data = (
                           ["54", "65", "73", "74"],      # hex data list
                           "Test"                         # ASCII data string
                          )
             otherwise return False and empty tuple
    """
    result = False
    event_data_raw = []
    event_data_str = ''
    event_idx = int(event_index) - 1
    event_idx = event_idx if event_idx >= 0 else 0

    if not os.path.exists(log_file):
        library.write_log(lib_constants.LOG_WARNING, "Log file %s does not exists" % log_file,
                          test_case_id, script_id, log_level, tbd)
        return result, ([], '')

    with codecs.open(log_file, 'r', encoding='ansi') as fp:
        info = fp.readlines()

    for idx in range(len(info)):
        # search event in log file
        if event.upper() in info[idx].upper():
            if event_idx > 0:
                event_idx -= 1
                continue

            library.write_log(lib_constants.LOG_INFO,
                              "%s event be present in logs" % event,
                              test_case_id, script_id,
                              log_level, tbd)
            # get number of bytes of event data
            idx += 3
            if idx >= len(info):
                library.write_log(lib_constants.LOG_WARNING,
                                  "Event data under %s event not be present in logs" % event,
                                  test_case_id, script_id,
                                  log_level, tbd)
                return result, ([], '')
            if "EventData".upper() in info[idx].upper():
                # get number of bytes, log shows as EventData (166 bytes):
                number_of_bytes = info[idx].split('(')[1].split(' ')[0]
                library.write_log(lib_constants.LOG_INFO,
                                  "Event data is %s bytes" % number_of_bytes,
                                  test_case_id, script_id,
                                  log_level, tbd)

            # start to parse data response to given event
            # data structure is as follows:
            # 00000000 | 18 d0 c1 3c 00 00 00 00-38 4f 17 00 00 00 00 00 |  ÐÁ<    8O
            # 00000010 | 00 00 00 10 00 00 00 00-86 00 00 00 00 00 00 00 |         †
            for data_idx in range(idx, len(info)):
                # the line start with **** points to next event, break the loop, like:
                # ****ID0001***0x1234-0x5678********************************************
                if info[data_idx].startswith("****") or info[data_idx].startswith("===="):
                    break
                if ' | ' in info[data_idx]:
                    data = info[data_idx].split(' | ')
                    # get hex raw data
                    # replace '-' to ' '
                    raw_data = data[1].replace('-', ' ')
                    # assemble raw data into a list, as:
                    # ["18", "d0", "c1", "3c", "00", "00", "00", "00",
                    #  "38", "4f", "17", "00", "00", "00", "00", "00"]
                    raw_data = raw_data.strip().split(' ')
                    event_data_raw.extend(raw_data)
                    # get ASCII data
                    ascii_data = data[2] if data[2] else ""
                    if data[2].endswith('\r\n'):
                        ascii_data = data[2].rstrip('\r\n')
                    elif data[2].endswith('\n'):
                        ascii_data = data[2].rstrip('\n')
                    event_data_str += ascii_data

            if len(event_data_raw) > 0:
                result = True
                library.write_log(lib_constants.LOG_INFO,
                                  "Event data under %s event be present in logs" % event,
                                  test_case_id, script_id,
                                  log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "Event data under %s event not be present in logs" % event,
                                  test_case_id, script_id,
                                  log_level, tbd)
            break
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "The %dth %s event not be present in logs" % (int(event_index), event),
                          test_case_id, script_id,
                          log_level, tbd)

    return result, (event_data_raw, event_data_str)


def is_pcr_value_equal(l_pcr_value, r_pcr_value, test_case_id, script_id, log_level="ALL", tbd="None"):
    """compare 2 PCR values, check whether they are equal
    :param l_pcr_value: left PCR value provided
    :param r_pcr_value: right PCR value provided
    :param test_case_id: test case id
    :param script_id: script id
    :param log_level: log level
    :param tbd: tbd
    :return: True if values equal, otherwise False
    """
    is_value_valid = True
    if l_pcr_value:
        library.write_log(lib_constants.LOG_INFO, "Left PCR value = {}".format(l_pcr_value),
                          test_case_id, script_id, log_level, tbd)
        l_pcr_value = int(l_pcr_value, 16)
    else:
        library.write_log(lib_constants.LOG_WARNING, "Left PCR value is invalid",
                          test_case_id, script_id, log_level, tbd)
        is_value_valid = False

    if r_pcr_value:
        library.write_log(lib_constants.LOG_INFO, "Right PCR value = {}".format(r_pcr_value),
                          test_case_id, script_id, log_level, tbd)
        r_pcr_value = int(r_pcr_value, 16)
    else:
        library.write_log(lib_constants.LOG_WARNING, "Right PCR value is invalid",
                          test_case_id, script_id, log_level, tbd)
        is_value_valid = False

    if not is_value_valid:
        return False
    else:
        return l_pcr_value == r_pcr_value


if __name__ == "__main__":
    file = r"C:\Testing\tbs.log"
    res, value = verify_event_and_pcr(file, "EV_EFI_PLATFORM_FIRMWARE_BLOB", "PCR[00]", "None", "None", event_index=3)
    print("Result of verify_event_and_pcr() is:")
    print(res)
    print("Value:")
    print(value)

    res, dat = get_event_data(file, "EV_EFI_PLATFORM_FIRMWARE_BLOB", "None", "None", event_index=5)
    print("Result of get_event_data() is:")
    print(res)
    print("Raw data:")
    print(dat[0])
    print("Data string:")
    print(dat[1])

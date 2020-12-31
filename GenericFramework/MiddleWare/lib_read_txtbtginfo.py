"""
File Name   : lib_read_txtbtginfo.py
Description : parse txtbtginfo logs, to get the register value
Author      : Jinliang
Created On  : 2 Mar 2020
"""
import os
import codecs

from SoftwareAbstractionLayer import utils, library, lib_constants
from MiddleWare.lib_bios_config import BiosMenuConfig
from MiddleWare.lib_get_val_from_log import determine_encoding_of_file

bios_conf_obj = BiosMenuConfig()


def get_txtbtg_config_info(component, log_to_save=None,
                           test_case_id="None", script_id="None",
                           loglevel="ALL", tbd="None"):
    """run txtbtginfo.efi tool in efi shell, return configuration info response to component list
    :param component: component specification. string containing any combination of the characters 'PCRHTFBA'
                          respectively indicates:
                          Processor, Chipset, Registers, Heap, TPM, FIT, Btg, and All.
    :param log_to_save: if provide, save info to log file; if not, skip
    :param test_case_id: test case ID
    :param script_id: script ID
    :param loglevel: log level
    :param tbd: tbd
    :return: a list with configuration info line by line
    """
    efi_file = utils.ReadConfig("TXTBTGTOOL", "EFI_FILE")
    # find correct efi file path in EFI sile system
    efi_file_path = bios_conf_obj.find_file_in_fs(efi_file)
    if efi_file_path is None:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: File %s not found" % efi_file,
                          test_case_id, script_id, loglevel, tbd)
        return False

    # executed command, e.g. TxtBtgInfo.efi -c P
    command = "%s -c %s" % (efi_file_path, component)
    info = bios_conf_obj.efi_shell_cmd(command)
    info = info.replace('\r', '')
    # save file while specify the file path
    if log_to_save:
        with open(log_to_save, 'w') as fp:
            fp.write(info)
            fp.close()
    # split info with '\n' to list
    info = info.split('\n')
    return info


def get_txtbtg_ac_module_info(log_to_save=None, test_case_id="None", script_id="None",
                              loglevel="ALL", tbd="None"):
    """run txtbtginfo.efi tool in efi shell, return AC module info list
    :param log_to_save: if provide, save info to file; if not, skip
    :param test_case_id: test case ID
    :param script_id: script ID
    :param loglevel: log level
    :param tbd: tbd
    :return: a list with AC module info line by line
    """
    efi_file = utils.ReadConfig("TXTBTGTOOL", "EFI_FILE")
    # find correct efi file path in EFI sile system
    efi_file_path = bios_conf_obj.find_file_in_fs(efi_file)
    if efi_file_path is None:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: File %s not found" % efi_file,
                          test_case_id, script_id, loglevel, tbd)
        return False

    command = "%s -a" % efi_file_path
    info = bios_conf_obj.efi_shell_cmd(command)
    info = info.replace('\r', '')
    # save file while specify the file path
    if log_to_save:
        with open(log_to_save, 'w') as fp:
            fp.write(info)
            fp.close()
    # split info with '\n' to list
    info = info.split('\n')
    return info


def verify_bit_range(start_bit, end_bit, highest_bit, lowest_bit):
    """Verify start bit and end bit is in the bit range, and start bit should great than end bit
    :param start_bit: high bit position
    :param end_bit: low bit position
    :param highest_bit: the highest bit of range
    :param lowest_bit: the lowest bit of range
    :return: True if verify succeed, otherwise False
    """
    if int(start_bit) > int(highest_bit) or int(start_bit) < int(lowest_bit):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: start bit is %d, out of range %d:%d"
                          % (int(start_bit), int(highest_bit), int(lowest_bit)),
                          "None", "None")
        return False

    if int(end_bit) > int(highest_bit) or int(end_bit) < int(lowest_bit):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: end bit is %d, out of range %d:%d"
                          % (int(end_bit), int(highest_bit), int(lowest_bit)),
                          "None", "None")
        return False

    if int(start_bit) < int(end_bit):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: start bit is %d, end bit is %d, "
                          "start bit must be great than/equal to end bit"
                          % (int(start_bit), int(end_bit)),
                          "None", "None")
        return False

    return True


def get_bit_value(value, start_bit, end_bit):
    """get a range of bit values from given value
    :param value: source value
    :param start_bit: high bit position
    :param end_bit: low bit position
    :return: bit value
    :rtype: str
    """
    # set mask, to start_bit - end_bit with 1's, e.g. 0b111111
    mask = 1
    for _ in range(int(start_bit) - int(end_bit)):
        mask <<= 1
        mask += 1

    # convert value to binary
    value = int(value, 16)
    # firstly move right end_bit bits, to remove the invalid part of the low position
    value >>= end_bit
    # and operation with mask
    new_value = value & mask
    return hex(new_value)


def read_registers_info(log_file, register, offset, start_bit, end_bit,
                        test_case_id="None", script_id="None",
                        loglevel="ALL", tbd="None"):
    """read registers information by TxtBtgTool
    :param log_file: log file to be parsed
    :param register: register type/name
    :param offset: offset value, should start with '0x', or end with 'h'
    :param start_bit: high bit position
    :param end_bit: low bit position
    :param test_case_id: test case ID
    :param script_id: script ID
    :param loglevel: log level
    :param tbd: tbd
    :return: register value in search range [start_bit:end_bit]
             False while register not be found
    :rtype: str
    """
    if not verify_bit_range(start_bit, end_bit, 63, 0):
        return False

    if not os.path.exists(log_file):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Not found %s" % log_file,
                          test_case_id, script_id, loglevel, tbd)
        return False

    # read file content to info list
    encode_format = determine_encoding_of_file(log_file, test_case_id,
                                               script_id, loglevel, tbd)
    fp = codecs.open(log_file, 'r', encoding=encode_format)
    info = fp.readlines()
    fp.close()

    for line in info:
        # skip empty line
        if line in ['\n', '\r\n']:
            continue
        # Skip the indented lines
        if line[0].isspace():
            continue
        if (register.upper() in line.upper() and
                offset.upper() in line.upper()):
            value = line.split(" ")[-1].strip()
            return get_bit_value(value, start_bit, end_bit)
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Not found %s register info with offset %s"
                          % (register, offset),
                          test_case_id, script_id, loglevel, tbd)
        return False


def read_fit_info(log_file, entry_index, entry_name, component,
                  test_case_id="None", script_id="None",
                  loglevel="ALL", tbd="None"):
    """read Firmware Interface Table information by TxtBtgTool, return component value of specified entry
    :param log_file: log file to be parsed
    :param entry_index: entry index
    :param entry_name: entry name, e.g. uCode Patch
    :param component: component of entry, e.g. Address
    :param test_case_id: test case ID
    :param script_id: script ID
    :param loglevel: log level
    :param tbd: tbd
    :return: component value; False while entry/component not be found
    :rtype: str
    """
    if not os.path.exists(log_file):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Not found %s" % log_file,
                          test_case_id, script_id, loglevel, tbd)
        return False

    # read file content to info list
    encode_format = determine_encoding_of_file(log_file, test_case_id,
                                               script_id, loglevel, tbd)
    fp = codecs.open(log_file, 'r', encoding=encode_format)
    info = fp.readlines()
    fp.close()

    for line in info:
        # get number of FIT entries
        if "Number of FIT entries" in line:
            entries_number = line.split("=")[-1].strip()
            if int(entry_index) >= int(entries_number) or int(entry_index) < 0:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Entry index %d is out of FIT entries range 0-%d"
                                  % (int(entry_index), int(entries_number)-1),
                                  test_case_id, script_id, loglevel, tbd)
                return False
        else:
            break

    # collect information of the specified entry
    entry_info = []
    for idx in range(len(info)):
        if (entry_name.upper() in info[idx].upper() and
                ("ENTRY %d" % int(entry_index)) in info[idx].upper()):
            # assign new list start with specified entry
            info = info[idx+1:]
            break
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Entry %d %s not be found"
                          % (int(entry_index), entry_name),
                          test_case_id, script_id, loglevel, tbd)
        return False

    for idx in range(len(info)):
        if info[idx].startswith("\n") or info[idx].startswith("\r\n"):
            # split by a blank line, preserving the previous information
            entry_info = info[:idx]
            break

    # traverse entry_info to get component value
    for line in entry_info:
        if component.upper() in line.upper():
            value = line.split(" ")[-1].strip()
            return value
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Component %s of Entry %d not be found"
                          % (component, int(entry_index)),
                          test_case_id, script_id, loglevel, tbd)
        return False


def read_chipset_info(log_file, component, test_case_id="None",
                      script_id="None", loglevel="ALL", tbd="None"):
    """read Firmware Interface Table information by TxtBtgTool, return component value of specified entry
    :param log_file: log file to be parsed
    :param component: component, e.g. MCH/IMC
    :param test_case_id: test case ID
    :param script_id: script ID
    :param loglevel: log level
    :param tbd: tbd
    :return: component value; False while component not be found
    :rtype: str
    """
    if not os.path.exists(log_file):
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Not found %s" % log_file,
                          test_case_id, script_id, loglevel, tbd)
        return False

    # read file content to info list
    encode_format = determine_encoding_of_file(log_file, test_case_id,
                                               script_id, loglevel, tbd)
    fp = codecs.open(log_file, 'r', encoding=encode_format)
    info = fp.readlines()
    fp.close()

    for idx in range(len(info)):
        if "CHIPSET INFORMATION" in info[idx].upper():
            info = info[(idx+1):]
            break

    for line in info:
        if component.upper() in line.upper():
            if "=" in line:
                return line.split("=")[-1].strip()
            elif ":" in line:
                return line.split(":")[-1].strip()
    else:
        library.write_log(lib_constants.LOG_WARNING,
                          "WARNING: Component %s not be found" % component,
                          test_case_id, script_id, loglevel, tbd)
        return False

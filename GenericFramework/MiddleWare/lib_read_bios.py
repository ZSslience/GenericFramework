__author__ = r"surajx/sushilx/tnaidux"

# Global Python Imports
import getopt
import csv
import os
import re
import sys
import time
from collections import deque
from xml.etree import ElementTree

# Local Python Imports
import library
import lib_constants
import lib_set_bios
import lib_xmlcli
import utils
sys.path.append(r"C:\Testing\GenericFramework\tools\pysvtools.xmlcli")
import pysvtools.xmlcli.XmlCli as cli

# GLobal Variable
bios_path = None

################################################################################
# Function Name   : xml_cli_read_bios
# Parameters      : ost, string_in_bios, tool, tc_id, script_id, log_level, tbd
# Functionality   : to read bios
# Return Value    : return True on success, False otherwise
################################################################################


def xml_cli_read_bios(ost, string_in_bios, tc_id, script_id,
                      log_level="ALL", tbd="None"):

    try:
        step = ost
        if "=" in step:
            option_in_bios = str(string_in_bios.split("=")[1]).strip()
            string_in_bios = (str(string_in_bios.split("=")[0])).strip()
        else:
            string_in_bios = string_in_bios.strip()
            option_in_bios = "None"

        if "virtual sensor participant 1" in string_in_bios.lower() and \
           "active thermal trip point" in string_in_bios.lower():
            string_in_bios = string_in_bios.lower().\
                replace("virtual sensor participant 1/", "")

        if "virtual sensor participant 2" in string_in_bios.lower() and \
           "active thermal trip point" in string_in_bios.lower():
            string_in_bios = string_in_bios.lower(). \
                replace("virtual sensor participant 2/", "")

        result = lib_xmlcli.read_bios_xmlcli(string_in_bios, option_in_bios,
                                             step, tc_id, script_id,
                                             log_level, tbd)

        if True in result:
            if "microcode revision" in string_in_bios.lower():
                result = list(result)
                result[1] = result[1] + "'h"
            return result
        else:
            if str(string_in_bios.split("/")[-1]) in lib_xmlcli.FORM_OPTIONS:
                return True, True
            else:
                return result
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
################################################################################
# Function Name : set_bios
# Parameters    : ostr, tool_name, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To set required bios path
################################################################################


def read_bios(ost, tool_name, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if "XMLCLI" == tool_name.upper():
            string_inbios = ost.lower().replace("read bios ", "")
            return xml_cli_read_bios(ost, string_inbios, tc_id, script_id,
                                    log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Read Bios "
                              "using %s tool is not implemented" % tool_name,
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hb:t:",)
    except getopt.GetoptError:
        print("Please use -h command for Help Message")
        print("Usage: lib_read_bios.py -h")
        return False

    try:
        if 0 == len(opts):
            print("Please use -h command for Help Message")
            print("Usage: lib_read_bios.py -h")
            return False
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print("##################################################\n")
                    print("Description:\n\tThis API aims at to read bios " \
                          "value for the required knob using Tools like " \
                          "XmlCli etc. This API internally performs set bios " \
                          "and verifies the value is set properly or not.\n")

                    print("Arguments:\n-h\n\t For printing the help message")

                    print("-b\n\t bios path e.g Set Bios /Bios/Intel advanced" \
                          " menu/ACPI settings/Low Power S0 Idle Capability =" \
                          " Disabled")

                    print("-t\n\t Tool name using which needs to read BIOS " \
                          "e.g XmlCli")

                    print("Usage:\n\tlib_read_bios.py -b '<bios_path>' " \
                          "-t <Tool Name> \n")
                    print("####################################################")
                    return True
                elif opt in "-b":
                    global bios_path
                    bios_path = arg
                elif opt in "-t":
                    tool_name = arg
                else:
                    return False
            read_bios(bios_path, tool_name, "Read_Bios", "Read_Bios",
                     log_level="ALL", tbd=None)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

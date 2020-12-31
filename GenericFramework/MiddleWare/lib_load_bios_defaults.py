__author__ = 'jkmody\sushil'

########################## General Imports #####################################
import os
from subprocess import Popen, PIPE
import codecs
import datetime
import sys
########################## Local Imports #######################################
import lib_constants
import lib_set_bios
import utils
import library
sys.path.append(r"C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli")
import pysvtools.xmlcli.XmlCli as cli

################################################################################
# Function Name   : xml_cli_enable
# Parameters      : test_case_id, script_id, log_level, tbd
# Functionality   : enables the xml cli support in BIOS
# Return Value    : Returns True if bios set to xmlcli support 
# 					or false on failure
################################################################################


def xml_cli_enable(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        cli.clb._setCliAccess("winsdk")
        result = cli.clb.ConfXmlCli()

        if 0 == result or 2 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli is already"
            " supported & enabled", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: XmlCli not "
            "enabled or supported", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Error: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)
    return False

################################################################################
# Function Name  : xml_cli_load_bios_defaults
# Parameters     : test_case_id, script_id, log_level, tbd
# Functionality  : load bios to default
# Return Value   : Returns True if bios set to defaults successfully,
#                  False otherwise
################################################################################


def xml_cli_load_bios_defaults(test_case_id, script_id, log_level="ALL",
                               tbd=None):

    try:
        cli.clb._setCliAccess("winsdk")
        result = cli.CvLoadDefaults()
        cli.clb.ConfXmlCli()

        if 0 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully set "
            "the setting to default", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
            "set default setting", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Error: Due to %s"%e,
        test_case_id, script_id, log_level, tbd)
    return False

################################################################################
# Function name : load_bios_defaults
# Description   : Code to load bios defaults
# Parameters    : test_case_id, script_id, log_level and tbd
# Returns       : True on successful action, False otherwise
######################### Main script ##########################################


def load_bios_defaults(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        result_flag = False
        
        if tbd.upper() in lib_constants.TBD_PLATFORM:
            os.chdir(lib_constants.EPCSTOOLPATH)
            command = "BIOSConf.exe updatedefaults"                             #Command for loading the bios defaults
            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            os.chdir(lib_constants.SCRIPTDIR)

            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_WARNINGR, "WARNING: Unable"
                " to load the bios Defaults due to %s "%str(stderr),
                test_case_id, script_id, "None", "None", log_level, tbd)        #Write the error to the log
                return False
            result_flag = True

        else:
            result_flag = xml_cli_load_bios_defaults(test_case_id, script_id,
                                                     log_level, tbd)

        if result_flag:
            return True                                                         #Returning True on Success
        else:
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Write the execption error to the log
        return False

################################################################################
# Function name  : set_state_after_g3
# Description    : Code to Set state after g3 to S5
# Parameters     : test_case_id, script_id, log_level and tbd
# Returns        : True on successful action, False otherwise
######################### Main script ##########################################


def set_state_after_g3(test_case_id, script_id, log_level="ALL", tbd=None):     #Function for setting state after G3 to S5

    try:
        string_in_bios = lib_constants.STATE_AFTER_G3_BIG_CORE
        ostr = string_in_bios

        result = lib_set_bios.\
            xml_cli_set_bios(ostr, string_in_bios, test_case_id, script_id,
                             log_level, tbd)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Bios option "
            "successfully set", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable "
            "to set bios option", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Write the execption error to the log
        return False

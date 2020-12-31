########################### General python imports #############################
import subprocess
import time
import os
########################## Local imports #######################################
import lib_constants
import utils
import library
import lib_xmlcli

################################################################################
# Function Name : set_Multiple_bootorder()
# Parameters    : token, tc_id, script_id
# Functionality : This function will set multiple boot order
# Return Value :  True/False
################################################################################

def set_multiple_bootorder(param, tc_id, script_id, log_level="ALL", tbd= None): # Function to set the boot order for 1 or n devices in order
    tool = "XmlCli"
    try:

        device_name = library.parse_variable(param, tc_id, script_id, log_level,
                                             tbd)

        if device_name is False:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to"
                              " read %s value from Config.ini" %param, tc_id,
                              script_id, "None", "None", log_level, tbd)
            return  False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Sucessfully read "
                             "device from config as %s" %device_name, tc_id,
                              script_id, "None", "None", log_level, tbd)        # Writes the error output to the log when unable to read the config value

        result = lib_xmlcli.set_boot_order(device_name, tc_id, script_id, tool,
                                           log_level, tbd)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully set %s"
                              " first in first boot order" % device_name, tc_id,
                              script_id, tool, lib_constants.STR_NONE,
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set"
                              " %s as first in boot order" % device_name,
                              tc_id, script_id, tool, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"Error: due to %s"%e,
                          tc_id,script_id,log_level,tbd)
        return False
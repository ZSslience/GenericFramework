__author__ = 'patnaikx'

############################General Python Imports##############################
import subprocess
import re
import os
############################Local Python Imports################################
import library
import lib_constants
import utils

################################################################################
# Function Name : get_keyboard_properties
# Parameters    : ostr - token, test_case_id-test case ID, script_id - script ID
# Functionality : get keyboard properties in control panel
# Return Value  : 'Keyboard property value' on successful action and 'False'
#                  on failure
# Syntax        : get <Keyboard_type> Keyboard property <property name>
################################################################################


def get_keyboard_properties(ostr, test_case_id, script_id, log_level="ALL",
                               tbd=None):
    try:
        token = ostr.upper().split(" ")                                         #set input token
        keyboard_type = token[1]                                                #store type of keyboard
        keyboard_property, pos = utils.extract_parameter_from_token(token,
                                            "PROPERTY","")                      #extract keyboard property from input token
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Value to be obtained "
        "for %s keyboard is %s"%(keyboard_type, keyboard_property),
        test_case_id, script_id, "None", "None", log_level, tbd)

        cmd_to_get_repeat_delay = lib_constants.KB_REPEAT_DELAY                 #command to get default repeat delay of keyboard
        cmd_to_get_repeat_rate = lib_constants.KB_REPEAT_RATE                   #command to get default repeat rate of keyboard
        current_repeat_delay = ""
        current_repeat_rate = ""

        if "REPEAT DELAY" == keyboard_property:
            current_repeat_delay = subprocess.check_output(cmd_to_get_repeat_delay,
                                shell=True)                                     #store current repeat delay value for keyboard
            current_repeat_delay = re.findall(r'\d+', current_repeat_delay)
            current_repeat_delay = current_repeat_delay[0]
            library.write_log(lib_constants.LOG_INFO,"INFO: Current "
            "rate delay value is %s"%current_repeat_delay, test_case_id,
            script_id, "None", "None", log_level, tbd)
            return current_repeat_delay

                                                          
        elif "RATE DELAY" == keyboard_property or "REPEAT RATE" == keyboard_propert:
            current_repeat_rate = subprocess.check_output(cmd_to_get_repeat_rate,
                                shell=True)                                     #store current repeat rate value for keyboard
            current_repeat_rate = re.findall(r'\d+', current_repeat_rate)
            current_repeat_rate = current_repeat_rate[0]
            library.write_log(lib_constants.LOG_INFO,"INFO: Keyboard repeat "
            "delay value is %s"%current_repeat_rate, test_case_id,
            script_id, "None", "None", log_level, tbd)
            return current_repeat_rate
        
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Unsupported input "
            "for keyboard property %s given"%keyboard_property, test_case_id,
            script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:                                                      #exception handled
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due to "
        "%s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
        return False





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
# Function Name : change_keyboard_properties
# Parameters    : ostr - token, test_case_id-test case ID, script_id - script ID
# Functionality : change keyboard properties in control panel
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : Change <Keyboard_type> Keyboard property <property name> to
#                <value to be set>
################################################################################


def change_keyboard_properties(ostr, test_case_id, script_id, log_level="ALL",
                               tbd=None):
    try:
        token = ostr.upper().split(" ")                                         #set input token
        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        log_path = lib_constants.SCRIPTDIR + "\\" + log_file
        keyboard_type = token[1]                                                #store type of keyboard
        keyboard_property, pos = utils.extract_parameter_from_token(token,
                                            "PROPERTY", "TO")                   #extract keyboard property from input token
        value, pos = utils.extract_parameter_from_token(token, "TO","")         #extract value to be change for keyboard property from input token

        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Value to be change "
        "for %s keyboard %s is %s"%(keyboard_type, keyboard_property, value),
        test_case_id, script_id, "None", "None", log_level, tbd)

        if "STEP" in value:                                                     #if value to be fetched from step of result.ini
            step = value.split(" ")[1]
            value = utils.read_from_Resultfile(step)                            #extract value from result file
            if value:
                library.write_log(lib_constants.LOG_INFO, "INFO: Value for "
                "%s keyboard %s extracted from result.ini"%(keyboard_type,
                keyboard_property), test_case_id, script_id, "None",
                "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "extract Value for %s keyboard %s from result.ini"%(
                keyboard_type, keyboard_property), test_case_id, script_id,
                "None", "None", log_level, tbd)
                return False
        else:
            pass
        cmd_set_kb_prop = lib_constants.KB_PROPERTY_SET                         #command to set keyboard property
        cmd_to_get_repeat_delay = lib_constants.KB_REPEAT_DELAY                 #command to get default repeat delay of keyboard
        cmd_to_get_repeat_rate = lib_constants.KB_REPEAT_RATE                   #command to get default repeat rate of keyboard
        cmd_get_kb_prop = lib_constants.KB_PROPERTY_GET                         #command to get keyboard property
        current_repeat_delay = ""
        current_repeat_rate = ""
        if "REPEAT DELAY" == keyboard_property:
            current_repeat_rate = subprocess.check_output(cmd_to_get_repeat_rate,
                                shell=True)                                     #store current repeat rate value for keyboard
            current_repeat_rate = re.findall(r'\d+', current_repeat_rate)
            current_repeat_rate = current_repeat_rate[0]
            final_cmd_set_kb_prop = cmd_set_kb_prop%(int(current_repeat_rate),
                                                      int(value))               #final command for set keyboard repeat delay by keeping repeat rate constant
        elif "REPEAT RATE" == keyboard_property or "RATE DELAY" == keyboard_property:
            current_repeat_delay = subprocess.check_output(cmd_to_get_repeat_delay,
                                shell=True)                                     #store current repeat delay value for keyboard
            current_repeat_delay = re.findall(r'\d+', current_repeat_delay)
            current_repeat_delay = current_repeat_delay[0]

            final_cmd_set_kb_prop = cmd_set_kb_prop %(int(value),
                                                      int(current_repeat_delay))#final command for set keyboard repeat rate by keeping repeat delay constant
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Wrong input for "
            "keyboard property type given", test_case_id,
            script_id, "None", "None", log_level, tbd)
            return False
        try:
            subprocess.check_output(final_cmd_set_kb_prop, shell=True)          #call final command for set keyboard property
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due to"
            " %s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Command for "
            "changing keyboard properties ran successully", test_case_id,
            script_id, "None", "None", log_level, tbd)
        final_cmd_get_kb_prop = cmd_get_kb_prop + " > " + log_file              #final command for storing keyboard property value to log file
        subprocess.Popen(final_cmd_get_kb_prop, shell=True)                     #run final command for getting keyboard property value
        current_repeat_rate = subprocess.check_output(cmd_to_get_repeat_rate,
                            shell=True)                                         #store current repeat rate value for keyboard
        current_repeat_rate = re.findall(r'\d+',current_repeat_rate)
        current_repeat_rate = current_repeat_rate[0]
        current_repeat_delay = subprocess.check_output(cmd_to_get_repeat_delay,
                            shell=True)                                         #store current repeat delay value for keyboard
        current_repeat_delay = re.findall(r'\d+', current_repeat_delay)
        current_repeat_delay = current_repeat_delay[0]
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: After "
        "changing of keyboard property, keyboard repeat delay is %s and "
        "rate delay is %s "%(current_repeat_delay, current_repeat_rate),
        test_case_id, script_id, "None", "None", log_level, tbd)
        if "REPEAT DELAY" == keyboard_property:                                 #if keyboard property is REPEAT DELAY
            if value == current_repeat_delay:                                   #if input value and current repeat delay matches
                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                "property %s changed to %s"%(keyboard_property, value),
                test_case_id, script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                "change the keyboard property %s to %s"%(keyboard_property,
                value), test_case_id, script_id, "None", "None", log_level, tbd)
                return False
        elif "REPEAT RATE" == keyboard_property or "RATE DELAY" == keyboard_property:                                #if keyboard property is REPEAT RATE
            if value == current_repeat_rate:                                    #if input value and current repeat rate matches
                library.write_log(lib_constants.LOG_INFO,"INFO: Keyboard "
                "property %s changed to %s"%(keyboard_property, value),
                test_case_id, script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                "change the keyboard property %s to %s"%(keyboard_property,
                value), test_case_id, script_id, "None", "None", log_level, tbd)
                return False

    except Exception as e:                                                      #exception handled
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due to "
        "%s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
        return False





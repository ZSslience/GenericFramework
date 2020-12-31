__author__ = 'patnaikx', 'mmakhmox'
############################General Python Imports##############################
import os
import subprocess
import time
import re
import codecs
############################Local Python Imports################################
import utils
import library
import lib_constants
################################################################################
# Function Name     : check_usbtree_port
# Parameters        : token, test_case_id, script_id,
#                     log_level="ALL", tbd="None"
# Purpose           : check usb port details and its capability and over current issue
# Return Value      : 'True' on successful action and 'False' on failure
# Syntax            : Check USB <param1> Port <param2> for <param3>
# Parameter handled : param1- SS, TYPE-C, param2- HS
################################################################################
def check_usbtree_port(token, test_case_id, script_id, log_level="ALL",
                                                                    tbd="None"):
    try:
        token_list = token.upper().split(' ')
        port_number = None
        usb_type, pos = utils.extract_parameter_from_token(token_list, "USB",
                                                        "PORT", log_level, tbd) #Extract the usb type from the token

        port_number,pos_speed = utils.extract_parameter_from_token(token_list,
                                            "PORT", "FOR",log_level, tbd)       #Extract the speed from the token if system is specified


        if "CONFIG-" in port_number.upper():
            port_number_tag = port_number.split("-")[1]
            port_number_value = port_number.split("-")[2]
            port_number = utils.ReadConfig(port_number_tag, port_number_value)

            if "FAIL:" in port_number:
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Unable to read"
                " value from Config.ini",test_case_id, script_id,log_level, tbd)# writes the error output to the log when unable to read the config value
                return False, "Unable to read value from config.ini"
            else:
                pass
        if "UNDER" in token_list:
            string_to_parse,pos_speed = utils.extract_parameter_from_token\
                (token_list, "FOR", "UNDER",log_level, tbd)
        else:

            string_to_parse,pos_speed = utils.extract_parameter_from_token\
                (token_list, "FOR", "",log_level, tbd)


        usb_tree_view = utils.ReadConfig("USB_TREE_VIEW", "EXE_FILE")           # usb tree view tool exe name fetching from config.ini
        usb_tree_view_dir = utils.ReadConfig("USB_TREE_VIEW", "tooldir")        # usb view directory fetching from config.ini
        if "FAIL" in [usb_tree_view,usb_tree_view_dir]:
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Failed to "
            "get the config entry under [USB_TREE_VIEW]",
            test_case_id, script_id, "None", "None", log_level, tbd)            #if failed to get config info, exit
            return False, "Failed to get config entry"
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:  config entry "
            " under [USB_TREE_VIEW] fetched", test_case_id, script_id,
            "None", "None", log_level, tbd)                                     #continue to remaining steps as config entry is fetched

        os.chdir(usb_tree_view_dir)
        log_file = os.path.join(
            lib_constants.SCRIPTDIR, script_id.replace(".py", ".txt"))
        command = usb_tree_view + " /R:" + log_file                             # command to generate usb tree view log

        os.system(command)
        os.chdir(lib_constants.SCRIPTDIR)
        if os.path.exists(log_file):                                            # check for usb tree view log exist or not
            library.write_log(lib_constants.LOG_INFO, "INFO: USB tree view  "
            "log is generated successfully", test_case_id, script_id,
            "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to generate"
            "USB tree view log", test_case_id, script_id,
            "None", "None", log_level, tbd)
            return False, "Failed to generate USB log"
        if "TYPE-C" in usb_type:                                                # if usb-type is TYPE-C
            port_number_ = format(int(port_number),
                                  lib_constants.HEXADECIMAL_CONVERTION)         # converting string type port number to hexadecimal port number
            with codecs.open(log_file,  encoding='utf-16') as f_:
                for i, line in enumerate(f_):
                    if "Connection Information V2" in line:                     # searching specific port information under Connection information

                        if ("Connection Index         : " +str(port_number_)\
                            + " ("+str(port_number)+")").lower() in next(f_).lower():                 # parsing usb tree view log for given port number
                            for i in range(12):
                                line = next(f_)
                                if string_to_parse.replace(" ","").strip("'").\
                                        lower() in line.replace(" ","").\
                                        strip().lower():                        # if string to be parse is found with specific port
                                    library.write_log(lib_constants.LOG_INFO,
                                    "INFO: %s number port of TYPE-C enabled "
                                    "is supported with %s feature"%\
                                                      (string_to_parse,\
                                                       port_number),test_case_id,
                                    script_id, "None", "None", log_level, tbd)
                                    return True, "Type-C Port is SS supported"

            library.write_log(lib_constants.LOG_INFO, "INFO: %s number port of "
            "TYPE-C enabled is not supported with %s feature "
            %(string_to_parse,port_number), test_case_id, script_id,
            "None", "None", log_level,tbd)
            return False, "Type-C enabled not supported"
        if "TYPE-A" in usb_type:                                                # if usb-type is TYPE-C
            port_number_ = format(int(port_number),
                                  lib_constants.HEXADECIMAL_CONVERTION)         # converting string type port number to hexadecimal port number
            with codecs.open(log_file, encoding='utf-16') as f_:
                for i, line in enumerate(f_):
                    if "Connection Information V2" in line:                     # searching specific port information under Connection information

                        if ("Connection Index         : " +str(port_number_)\
                            + " ("+str(port_number)+")").lower() in next(f_).lower():                 # parsing usb tree view log for given port number
                            for i in range(12):
                                line = next(f_)
                                if string_to_parse.replace(" ","").strip("'").\
                                        lower() in line.replace(" ","").\
                                        strip().lower():                        # if string to be parse is found with specific port
                                    library.write_log(lib_constants.LOG_INFO,
                                    "INFO: %s number port of TYPE-A enabled "
                                    "is supported with %s feature"%\
                                                      (string_to_parse,\
                                                       port_number),test_case_id,
                                    script_id, "None", "None", log_level, tbd)
                                    return True, "Type-A enabled  supported"

            library.write_log(lib_constants.LOG_INFO, "INFO: %s number port of "
            "TYPE-A enabled is not supported with %s feature "
            %(string_to_parse,port_number), test_case_id, script_id,
            "None", "None", log_level,tbd)
            return False, "Type-A enabled not supported"

        elif "SS" in usb_type.upper() and 'IS PORT DEBUG CAPABLE' \
                in string_to_parse.upper():                                     #If port type is SS(superspeed) and searching for debug capable port
            with codecs.open(log_file, encoding='utf-16') as f_:                #Opening file with utf-16 decoding otherwise it will give junk data
                main_port_list = []
                flag = False
                for line in f_:
                    re_fetch = re.search('Port Chain.*:.(\d+)-(\d+)(-(\d+))?',
                                         line, re.I)                            #Searching for all root port
                    if None != re_fetch:
                        if None == re_fetch.group(3):
                            flag = True
                            port_list=[]
                            port_list.append(line)
                            status = False
                            for i in f_:
                                if 'SupportedUsbProtocols' in i:
                                    if '0x03' in i:                             #If port is highspeed(usb2.0), then skip
                                        status = False
                                        break
                                    elif '0x04' in i:                           #If port is superspeed (usb3.0), append all SS port
                                        port_list.append(i)
                                        break
                                if 'PortIsDebugCapable' in i:                   #Checking all ss port is debug capable or not
                                    if 'no' in i:
                                        status=True
                                if 'USB Port' in i:
                                    break
                                port_list.append(i)
                            if status:
                                main_port_list.append(port_list)
                            else:
                                pass
                if 0 == len(main_port_list) and flag:                                    #If list of ss port with no debug capable is empty, return True
                    library.write_log(lib_constants.LOG_INFO, "INFO: All SS"
                    "(superspeed) ports are debug capable in USB tree view tool"
                    " log ", test_case_id, script_id, "None", "None",
                    log_level, tbd)
                    message = "PASS: USB port details and capability are " \
                              "verified successfully"
                    return True, message
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s \nSS "
                        "(superspeed) ports are not debug capable in USB tree"
                        " view tool " %main_port_list, test_case_id, script_id,
                        "None", "None", log_level, tbd)
                    message = "FAIL: Failed to verify USB port details and " \
                              "its capability"
                    return False, message

        elif 'OVERCURRENT ISSUE' in string_to_parse.upper():                    #If overcurrent issue in string_to_parse
            flag = False
            with codecs.open(log_file, encoding='utf-16') as f_:                #Opining usbtreeview log file with utf-16 decoding.
                flag = False
                for line in f_:
                    if "DEVICE FAILED ENUMERATION" in line.upper() \
                            or "DEVICEFAILEDENUMERATION" in line.upper():       #Checking for overcurrent issue
                        flag = True

                    if flag == True:
                        port_flag = False
                        if "HS" in usb_type.upper():                            #Checking for HS port
                            if "USB300" in line.upper() and "NO" in line.upper():
                                port_flag = True
                            else:
                                port_flag = False
                        else:
                            if "USB300" in line.upper() and "YES" in line.upper(): #Checking for SS port
                                port_flag = True
                            else:
                                port_flag = False

                        if port_flag:
                            library.write_log(lib_constants.LOG_INFO, "INFO: %s"
                                " ports found device failed enumeration due to"
                                " over-current issue in USB tree view tool"
                                %(usb_type), test_case_id, script_id, "None",
                                "None", log_level, tbd)                         #Writing to log as overcurrent issue found
                            message = "PASS: Device not enumerating due" \
                                      " to over current issue"
                            return True, message
                    else:
                        pass

                library.write_log(lib_constants.LOG_INFO, "INFO: Over-"
                    "current issue not seen on any %s "                         #Writing to log as overcurrent issue not found
                    "ports in USB tree view tool log "%(usb_type), test_case_id,
                    script_id, "None", "None", log_level, tbd)
                message = "FAIL: Over current issue not found on any ports."                                 #Pass message to return main script
                return False, message
        else:                                                                   #Returning with Fail message and False
            message = "FAIL: May be this option not yet handled please" \
                      " contact developer"
            return False, message

    except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception "
            "due to %s"%e, "None", log_level, tbd)                              #Writing log message which caught exception
            return False, "Exception Occured"

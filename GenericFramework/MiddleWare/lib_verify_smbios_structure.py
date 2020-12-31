__author__ = "kapilshx"

###########################General Imports######################################
import os
import platform
import string
import sys
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_tool_installation
################################################################################
# Function Name : smbios_table_type
# Parameters    : verify_smbios_token,log_file_smibos_path,testcaseid,
#                 scriptid, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : To verify smbios structure from smbiso table dump from EDK
#                shell
################################################################################
def verify_smbios_structure(verify_smbios_token,log_file_smibos_path,
    test_case_id, script_id,loglevel = "ALL", tbd="None"):
    try:
        if "royal park version" in verify_smbios_token.lower():                 #if "royal park version" is present in verify_smbios_token
            royal_park_version_config = utils.\
                ReadConfig("SMBIOS_VERSION","royal_park_version")               #read royal_park_version from config.ini file
            if "FAIL" in royal_park_version_config:                             #if Fail to read royal_park_version from config.ini file
                library.write_log(lib_constants.LOG_INFO,"INFO:Config entry"
                    " is missing for tag variable royal_park_version_config ",
                    test_case_id,script_id,"None","None",loglevel,tbd)          #write info msg to log
                return False
            else:
                pass
            row_smbios = []
            with open(log_file_smibos_path,'r',) as smbios_fp:                  #to open log_file_smibos_path file in read mode
                smbios_fp_lines = smbios_fp.readlines()
            for index,item in enumerate(smbios_fp_lines):                       #loop to parse royal_park_version from log_file_smibos_path file
                if "roy" in str(item).lower() or "royal" in str(item).lower():
                    finaltable = (smbios_fp_lines[index+1].
                                  split("*")[1]).split("*")[0] +\
                                 (smbios_fp_lines[index+2].split("*")[1]).\
                                  split("*")[0]
                    finaltable = ((finaltable.split("on.")[1]).
                                  split(".P")[0]).strip(" ")
                    row_smbios.append(finaltable)
                    break
                else:
                    pass
            royal_park_version_smbios = "".join(str(e) for e in row_smbios)     # convert royal_park_version_smbios into string
            if royal_park_version_config == royal_park_version_smbios:          # to compare royal_park_version_smbios with royal_park_version_config
                library.write_log(lib_constants.LOG_INFO,"INFO:Royal"
                    " park version is matching from config & smbios "
                "structure ",test_case_id,script_id,"None","None",loglevel,tbd) #write info msg to log
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO:Failed"
                " to match royal park version from config & smbios "
            "structure ",test_case_id,script_id,"None","None",loglevel,tbd)     #write info msg to log
                return False
        elif "verify smbios structure"  == verify_smbios_token.lower():         #if "verify smbios structure" is present in verify_smbios_token
            dict_smbios = {"type=0,":"structure type: bios information",
                        "type=1,":"structure type: system information",
                    "type=3,":"structure type: system enclosure",
                    "type=4,":"structure type: processor information",
                    "type=14,":"structure type: group associations",
                    "type=16,":"structure type: physical memory array",
                "type=17,":"structure type: memory device",
                    "type=19,":"structure type: memory array mapped address"}   #dictionary for mapping of type name with structure type information
            list_smbios = []
            for smbios_type_key in list(dict_smbios.keys()):                          #loop to iterate the all dictionary keys
                smbios_type_value = dict_smbios[smbios_type_key]
                result = find_structure_type(log_file_smibos_path,
                               smbios_type_key,smbios_type_value,test_case_id,
                           script_id,loglevel,tbd)                              #library calls to function find_structure_type
                list_smbios.append(str(result))                                 #to append all the result into list_smbios
            if "False" in list_smbios:                                          #if anyone "False" is present in the list_smbios
                return False
            else:                                                               #if ALL "True" is present in the list_smbios
                return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO:Input syntax is"
            " incorrect for verify smbios structure ",
                test_case_id,script_id,"None","None",loglevel,tbd)              #write info msg to log
            return   False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
            "verify_smbios_structure library function: %s"%e, test_case_id,
                script_id, "None","None", loglevel, tbd)                        #write error msg to log
        return False
################################################################################
# Function Name : find_structure_type
# Parameters    : log_file_smibos_path,smbios_type_key, smbios_type_value,
#                 scriptid,test_case_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : To map stucture type for given type value
################################################################################
def find_structure_type(log_file_smibos_path,smbios_type_key,smbios_type_value,
                        test_case_id, script_id,loglevel = "ALL", tbd="None"):
    try:
        with open(log_file_smibos_path,'r',) as smbios_fp:                      # to open file log_file_smibos_path in read mode
            smbios_fp_lines = smbios_fp.readlines()
        for index,item in enumerate(smbios_fp_lines):                           #loop to map stucture type for given type value
            if smbios_type_key in str(item).lower():                            #to check if smbios_type_key is present in the file
                index_start = index
                for item_type in smbios_fp_lines:
                    index_start += 1
                    if smbios_type_value in str(smbios_fp_lines[index_start]).\
                            lower():                                            #to check if smbios_type_value is present in the file
                        return True
                    elif "type=" in str(smbios_fp_lines[index_start+1]).lower():#to check if "type=" is present in the file
                        return False
                    else:
                        pass
            else:
                pass
        smbios_fp.close()
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
            "find_structure_type library function: %s"%e, test_case_id,
                script_id, "None","None", loglevel, tbd)                        #write error msg to log
        return False
################################################################################
__author__ = "sushil3x"

############################Local imports#######################################
import lib_constants
import library
import utils
import lib_read_bios
################################################################################
# Function Name : verify_capsule_update
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : true or false
# Functionality : to check Project Version, EC FW Version
################################################################################

def verify_capsule_update(test_case_id,script_id,log_level="ALL",tbd="None"):   #function for capsule update check
    try:
        if "GLK" == tbd.upper():
            ifwi_ver = utils.ReadConfig("capsule_create", "ifwi_version")       #Reading ProjectVersion from config.ini file
            ksc_ver = utils.ReadConfig("capsule_create", "kscversion")          #Reading EC Firmware Version from config.ini file

            cur_dir = lib_constants.SCRIPTDIR

            if "FAIL:" in [ifwi_ver, ksc_ver]:
                library.write_log(lib_constants.LOG_INFO,"INFO: Config entry "
                    "not found", test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         #fail if config entry is missing
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Config entry "
                    "found\\nProject Version : %s"
                    "\\nKSC Version : %s" %(ifwi_ver,ksc_ver),test_case_id,
                        script_id, "None", "None", log_level, tbd)              #pass if config entry is correct

                                                                                # Reading bios for IFWI version & KSC Version

            flag_ifwi_ver, capsule_ifwi_ver = lib_read_bios.\
                read_bios(lib_constants.GLK_IFWI_VER, test_case_id, script_id,
                    cur_dir, log_level, tbd)

            flag_ifwi_ver, capsule_ksc_ver = lib_read_bios.\
                read_bios(lib_constants.GLK_KSC_VER,test_case_id, script_id,
                    cur_dir, log_level, tbd)

            capsule_update_check = [flag_ifwi_ver,flag_ifwi_ver]
            capsule_update_check_flag = True

            for capsule_update_check_item in capsule_update_check:              # Checking bios read is successful or not
                if 7 != capsule_update_check_item:
                    capsule_update_check_flag = False
                    break
                else:
                    continue

            if True == capsule_update_check_flag:
                library.write_log(lib_constants.LOG_INFO, "INFO: Bios read "
                    "successful", test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         # Write pass info to log
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to read"
                    " bios", test_case_id, script_id, "None", "None", log_level,
                        tbd)                                                    # Write Fail info to log
                return False

            if ifwi_ver in capsule_ifwi_ver and ksc_ver in capsule_ksc_ver:     # Comparision of Config entry variable  & bios varialbe
                library.write_log(lib_constants.LOG_INFO,                       # i.e. Project Version,EC FW Version
                    "INFO: bios version & ksc version comparision passed"
                    ,test_case_id,script_id,"None","None",log_level,tbd)        # If values of Config variable & bios variable match then pass
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,
                    "INFO: bios version & ksc version comparision failed"
                    ,test_case_id,script_id,"None","None",log_level,tbd)        # If values of Config variable & bios variable doesn't match then fail
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Platform not "
                "handle", test_case_id, script_id, "None", "None", log_level,
                    tbd)                                                        # If platform not handle, return fail message
            return False


    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Error during "
            "comparison" +str(e), test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 # Exception error catch if failed
        return False
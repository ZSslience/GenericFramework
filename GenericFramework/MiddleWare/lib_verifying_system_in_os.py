__author__ = 'yusufmox'
###########################General Imports######################################
import os
############################Local imports#######################################
import lib_constants
import library
################################################################################
# Function Name : verifying_system_in_os
# Parameters    : state_token, platform, test_case_id, script_id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : To verify system is in <OS/EDK SHELL/BIOS>
################################################################################


def verifying_system_in_os(state_token, test_case_id, script_id,
                           loglevel="ALL", tbd="None"):

    try:
        if "BIOS SETUP" == state_token.upper():
            post_code_verify = lib_constants.BIOS_PAGE_POSTCODE
        elif "EDK SHELL" == state_token.upper():
            post_code_verify = lib_constants.EFI_POSTCODE
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: state %s to "
                              "be verifed is not handled" % state_token,
                              test_case_id, script_id, "TTK2", "None", loglevel,
                              tbd)
            return False

        if library.check_for_post_code(post_code_verify, lib_constants.TWO_MIN,
                                       test_case_id, script_id, loglevel, tbd):
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "verifed system is in %s" % state_token,
                              test_case_id, script_id, "TTK2", "None", loglevel,
                              tbd)
            return True

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to Verify"
                              " system is in %s" % state_token, test_case_id,
                              script_id, "TTK2", "None", loglevel, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          test_case_id, script_id, "TTK2", "None", loglevel,
                          tbd)                                                  #Write the exception occur in the library function verifying_system_in_os()
        return False

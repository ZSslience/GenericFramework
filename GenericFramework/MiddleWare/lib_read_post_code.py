__author__ = 'bisweswx'

###########################Local Imports########################################
import library
import lib_constants
import utils
import lib_ttk2_operations
################################################################################
# Function Name : read_post_code
# Parameters    : check_postcode = default to read current post code
#                 else check_postcode = post code to verify
# Functionality : Reading the current post code from Port80 using ttk
# Return Value  : True for successful post code checking
#                 False for post code checking fail/ TTK error
################################################################################
def read_post_code(ostr,test_case_id,script_id, loglevel,
                   tbd = None):


    try:

        if '=' in ostr:                                                         #if grammar expects post code to be verified e.g Read
            check,pos = library.extract_parameter_from_token(ostr,"=","")      #the post code = 0000,extracting the PC to check
            if "CONFIG-" in check.upper():                                      #Handles config in syntax, extracts the value from config file
                check_postcode = utils.configtagvariable(check)
            else:
                check_postcode = check
        else:
            check_postcode = 'default'

        current_postcode = lib_ttk2_operations.read_post_code(test_case_id,
                                                              script_id,
                                                              loglevel,
                                                              tbd)                             #read_post_code() return the current postcode
        if not '' == current_postcode:
            if (lib_constants.FFFF_POSTCODE).lower() == current_postcode:       #if post code is FFFF return false
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Post code read "
                              "successfully",test_case_id,script_id, "None",
                              "None", loglevel, tbd)
        else:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Postcode read "
            "failed",test_case_id,script_id,"None", "None", loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in TTK "
                          "operation",test_case_id,script_id,"None","None",
                          loglevel, tbd)
        return False
    if 'default' == check_postcode:                                             #if requirement is to only check the current post code,
                                                                                #default indicates that current postcode is to be read
        library.write_log(lib_constants.LOG_INFO,"PASS: Current Post code is %s"
                          %str(current_postcode),test_case_id,script_id,"None",
                          "None",loglevel,tbd)
        utils.write_to_Resultfile(current_postcode,script_id)
        return True
    else:                                                                       #if requirement is to compare current post code with the expected postcode
        if check_postcode.lower() == str(current_postcode):                     #if current postcode matches required postcode,converting to lower case as ttk return postcode in lower case
            library.write_log(lib_constants.LOG_INFO,"PASS: Given Post code"
                              "  %s matches current post code %s"
                              %(check_postcode.upper(),
                              str(current_postcode).upper()),
                              test_case_id,script_id, "None","None",loglevel,
                              tbd)
            return True
        else:                                                                   #if post codes are not matching this will return fail
            library.write_log(lib_constants.LOG_INFO,"FAIL: Given Post code %s "
                              "does not matches current post code %s"
                              %(check_postcode,current_postcode),test_case_id,
                              script_id,"None","None",loglevel,tbd)
            return False

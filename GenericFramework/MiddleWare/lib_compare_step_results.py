###########################Global Library imports###############################
import os
import re
import sys
import time
###########################Local Library imports################################
import lib_constants
import library
import utils
################################################################################


def binary_to_decimal(num):                                                     #Function for to convert binary to decimal
    num = num.replace("'b", "")
    num = int(num, 2)
    return num


def hexa_to_decimal(num):                                                       #Function for to convert hexa to decimal
    num = num.replace("'h", "")
    num = int(num, 16)
    return num


def number_conversion(num):
    if num[-1].lower() in lib_constants.NUMBER_CONVERSION_ALPHABETS and \
       num[-1].lower() not in lib_constants.NOT_IN_NUMBER and \
       num == num.isalnum():
        num = "0x" + num

    if "'b" in num:
        return binary_to_decimal(num)                                           #Converting binary to int
    elif "'h" in num or "0x" in num or "0X" in num:
        return hexa_to_decimal(num)                                             #Converting hexa to int
    elif "'d" in num:
        return int(round(float(num.replace("'d", ""))))                         #Converting decimal to int
    elif "00000000000" in num:                                                  #For PCR values to be treated as it is
        return int(num)
    elif "%" in num:
        return int(num.split("%")[0])
    elif "MHZ" in num.upper():                                                  #If mhz exists in number, split the number with space and return the same number
        return int(num.split(" ")[0])
    elif "GB" == num.upper().split(" ")[-1]:
        num = str((int(num[0]) * lib_constants.GB_SIZE))
        return num + " mb"
    else:
        if num.count(".") >= 2 or "GHZ" in num.upper() or num.isalpha() or \
           "/" in num or " " in num or "MB" in num.upper() or \
           re.search('[a-zA-Z]', num):                                          #If number having more than one '.', returning the number itself [ex: 12.0.0.1010 returning the same] or ghz or mb or space or '/' in number or every character in number is alphabet
            return num
        else:
            try:
                return int(round(float(num)))
            except:
                return (num)


def compare_value(lhs, rhs, operator, test_case_id, script_id, loglevel, tbd):

    try:
        if operator in ["=", "=="]:                                             #Check for == or =. If 2 string/ numbers are equal and set res_flag
            if ((str(lhs)).replace(" ", "")) == ((str(rhs)).replace(" ", "")):
                res_flag = True
            else:
                res_flag = False

        elif operator in ["!=", "<>"]:                                          #Check for != or <>. If 2 string/ numbers are unequal and set res_flag
            if lhs != rhs:
                res_flag = True
            else:
                res_flag = False

        elif ">" == operator:                                                   #Check for >. If lhs > rhs and set res_flag
            if lhs > rhs:
                res_flag = True
            else:
                res_flag = False

        elif ">=" == operator:                                                  #Check for >=. If lhs >= rhs and set res_flag
            if lhs >= rhs:
                res_flag = True
            else:
                res_flag = False

        elif "<" == operator:                                                   #Check for <. If lhs < rhs and set res_flag
            if lhs < rhs:
                res_flag = True
            else:
                res_flag = False

        elif "<=" == operator:                                                  #Check for <=. If lhs <= rhs  and set res_flag
            if lhs <= rhs:
                res_flag = True
            else:
                res_flag = False

        elif "contains" == operator.lower():
            lhs = str(lhs)
            rhs = str(rhs)
            if "'" in rhs:
                rhs = rhs.replace("'"," ")
            if str(rhs).lower() in str(lhs).lower():
                res_flag = True
            else:
                res_flag = False

        else:                                                                   #Tag as invalid operator  and set res_flag
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
            "operator", test_case_id, script_id, "None", "None", loglevel, tbd) #Writing log warning message to the log file
            res_flag = False

        return res_flag

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", loglevel, tbd)                 #Writing exception message to the log file
        return False


################################################################################
# Function Name : lib_compare_step_results
# Parameters    : test_case_id, script_id, lhs, operator, rhs, log_level and tbd
# Return Value  : Returns 1 if "PASS" and 0 if "FAIL" in comparison
# Functionality : Compares the values of step m with step n / configvar value /
#                 direct value
################################################################################


def lib_compare_step(test_case_id, script_id, step_no, operator, ostr, loglevel,
                     tbd):                                                      #Function definition for compare step result grammar

    lhs = str(utils.read_from_Resultfile((int(step_no))))                       #token[5] is the step number. Retrieve the step # value from result.ini

    if "CSSESSION1" in lhs.upper():
        lhs = lhs.strip(' ').split(',')
        for item in lhs:
            if "%" in item:
                lhs = item.strip('%')

    elif '|' in lhs or "PCR" in lhs:
        val_ret = lhs.split('|')[2].strip()
        match = lhs.split('|')[3].strip()
        lhs_val = (ostr.split(operator.lower()))[1].strip()                     #If token[7] is neither a config value or a step result, consider it as the direct value for comparison.
        if "MATCH" in lhs_val:
            lhs = match
        else:
            lhs = val_ret

    elif "," in lhs and " " in lhs and '"' in lhs:
        lhs = lhs.strip(', "')
    elif "GT" in lhs.upper() and "(" in lhs and ")" in lhs:
        lhs = lhs.split(" ")[-1].replace("(", "").replace(")", "")
    elif " " in lhs and "%" in lhs:
        lhs = lhs.split(" ")[-1]
    else:
        pass

    try:
        if "0" != str(lhs.lower())[0]:
            lhs = number_conversion(lhs.lower())
        elif "'b" in str(lhs.lower()) or "0x" in str(lhs.lower()) \
            or "'h" in str(lhs.lower()) or "'d" in str(lhs.lower()):
            lhs = number_conversion(lhs.lower())
        else:
            lhs = lhs.lower()
    except Exception as e:
        lhs = lhs.lower()

    if "not present in result.ini" in str(lhs).lower():
        library.write_log(lib_constants.LOG_INFO, "INFO: " + str(lhs) +
        " Hence comparision failed.", test_case_id, script_id, "None", "None",
        loglevel, tbd)                                                          #Writing log info message to the log file
        return False

    token = utils.ProcessLine(ostr)
    if "CONFIG" in token[7]:                                                    #token[7] is the RHS. Check if it is a config var and retrieve its value from config.ini
        (config, section, key) = token[7].split("-")
        rhs_val = str(utils.ReadConfig(section, key))
        if "FAIL" in rhs_val:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config Entry"
            " is not updated. Hence Comparision failed.", test_case_id,
            script_id, "None", "None", loglevel, tbd)                           #Writing log warning message to the log file
            return False



    elif "STEP" in token[7]:
        step_no = token[8]
        rhs_val = str(utils.read_from_Resultfile((int(step_no))))                    #token[8] is the step number. Retrieve the step # value from result.ini
        if "not present in result.ini" in rhs_val.lower():
            library.write_log(lib_constants.LOG_WARNING, "WARNING: " +
            str(rhs_val) + " Hence Comparision failed.", test_case_id,
            script_id, "None", "None", loglevel, tbd)                           #Writing log warning message to the log file
            return False

    else:
        rhs_val = (ostr.split(operator.lower()))[1].strip()                     #If token[7] is neither a config value or a step result, consider it as the direct value for comparison.
        if rhs_val.endswith("'") and rhs_val.startswith("'"):
            rhs_val = rhs_val.strip("'")
        elif rhs_val.endswith('"') and rhs_val.startswith('"'):
            rhs_val = rhs_val.strip('"')

    if '|' in rhs_val or "PCR" in rhs_val:
        val_ret = rhs_val.split('|')[2].strip()
        match = rhs_val.split('|')[3].strip()
        rhs_val = (ostr.split(operator.lower()))[1].strip()
        if "MATCH" in rhs_val:
            rhs_val = match
        else:
            rhs_val = val_ret

    if "GT" in rhs_val.upper() and "(" in rhs_val and ")" in rhs_val:
        rhs_val = rhs_val.split(" ")[-1].replace("(", "").replace(")", "")

    if " OR " in rhs_val.upper():
        rhs_val=rhs_val.upper().split(" OR ")
        res_flag = False
        for i in range(len(rhs_val)):
            rhs=number_conversion(str(rhs_val[i].strip().lower()))
            time.sleep(lib_constants.FIVE_SECONDS)
            result = compare_value(lhs, rhs, operator, test_case_id, script_id,
                                   loglevel, tbd)
            if True == result:
                res_flag = True
                break
    else:
        try:
            if "0" != str(rhs_val.lower())[0]:
                rhs = number_conversion(str(rhs_val.lower()))
            elif "'b" in str(rhs_val.lower()) or "0x" in str(rhs_val.lower()) \
                or "'h" in str(rhs_val.lower()) or "'d" in str(rhs_val.lower()):
                rhs = number_conversion(str(rhs_val.lower()))
            else:
                rhs = rhs_val.lower()

        except Exception as e:
            rhs = rhs_val.lower()

        time.sleep(lib_constants.FIVE_SECONDS)
        res_flag = compare_value(lhs, rhs, operator, test_case_id, script_id,
                                 loglevel, tbd)

    library.write_log(lib_constants.LOG_INFO, "INFO: Value to be compared with"
    "(lhs) is: "+str(lhs), test_case_id, script_id, "None", "None", loglevel,
    tbd)                                                                        #Writing log info message to the log file

    library.write_log(lib_constants.LOG_INFO, "INFO: Value to be compared(rhs)"
    " is: "+str(rhs), test_case_id, script_id, "None", "None", loglevel, tbd)   #Writing log info message to the log file

    library.write_log(lib_constants.LOG_INFO, "INFO: Comparision Operator is: "
    +operator, test_case_id, script_id, "None", "None", loglevel, tbd)          #Writing log info message to the log file

    if True == res_flag:                                                        #If res_flag is true write success message in the log
        library.write_log(lib_constants.LOG_INFO, "INFO: " + str(lhs) + " " +
        operator + " " + str(rhs) + " Valid expression", test_case_id,
        script_id, "None", "None", loglevel, tbd)                               #Writing log info message to the log file
        return True
    else:                                                                       #If res_glag is false, write failure message in the log
        library.write_log(lib_constants.LOG_WARNING, "WARNING: " + str(lhs) +
        " " + operator + " " + str(rhs) + " Invalid expression", test_case_id,
        script_id, "None", "None", loglevel, tbd)                               #Writing log warning message to the log file
        return False


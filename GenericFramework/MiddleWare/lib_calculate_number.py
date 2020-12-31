############################General Python Imports##############################
import os
import sys
import time
import math
############################Local Python Imports################################
import utils
import library
import lib_constants
################################################################################
# Function Name : binary_to_decimal
# Parameters    : num- number in binary format
# Functionality : Performs conversion of binary to float
# Return Value  : will return the float value
################################################################################


def binary_to_decimal(num):
    num = num.replace("'B", "")
    num = float(int(num, 2))                                                    #Converting binary to float
    return num

################################################################################
# Function Name : hexa_to_decimal
# Parameters    : num- number in Hexadecimal format
# Functionality : Performs conversion of Hexadecimal to float
# Return Value  : will return the float value
################################################################################


def hexa_to_decimal(num):
    if "'H" in num:
        num = num.replace("'H", "")
    num = float(int(num, 16))                                                   #Converting hexa to float
    return num

################################################################################
# Function Name : number_conversion
# Parameters    : num- number in Binary/Hexadecimal/Decimal format
# Functionality : Performs conversion of Binary/Hexadecimal/Decimal to float
# Return Value  : will return the int value
################################################################################


def number_conversion(num):
    if "'B" in num:
        return binary_to_decimal(num)                                           #Calling function for Converting binary to float
    elif "'H" in num or "0X" in num:
        return hexa_to_decimal(num)                                             #Calling function for Converting hexa to float
    elif "'D" in num:
        return float(num.replace("'D", ""))                                #Calling function for Converting decimal to float
    elif "MHZ" in num:
        return float(num.replace("MHZ", ""))
    else:
        if num.isalpha() or "/" in num or " " in num:
            return num
        else:
            return int(round(float(num)))

################################################################################
# Function Name : calculate_number
# Parameters    : TC_id-test case ID, script_id  - script ID,
#                 token - token
# Functionality : Performs Arithmetic Functionality
# Return Value  : 'Value' on successful action and 'False' on failure
# Syntax        : Calculate <value1> <Arithmetic Operator> <Value2>
################################################################################


def calculate_number(tc_id, script_id, token,  log_level, tbd=None):

    tc_id = tc_id
    script_id = script_id

    if "CONFIG" in token[1]:                                                    #Token[1] is the LHS. Check if it is a config var and retrieve its value from config.ini
        (config, section, key) = token[1].split("-")
        lhs_val = utils.ReadConfig(section, key)
        operator = token[2]

    elif "STEP" in token[1]:
        step_no = token[2]
        lhs_val = utils.read_from_Resultfile((int(step_no)))                    #Token[2] is the step number. Retrieve the step # value from result.ini
        operator = token[3]
    else:
        lhs_val = token[1]
        operator = token[2]

    param2, end_pos = utils.extract_parameter_from_token(token, operator, "",
                                                         log_level, tbd)
    if "CONFIG" in param2:                                                      #Param2 is the RHS. Check if it is a config var and retrieve its value from config.ini
        (config, scetion, key) = param2.split("-")
        rhs_val = utils.ReadConfig(scetion, key)
    elif "STEP" in param2:                                                      #Param2 is the RHS. Check if it is a step var and retrieve its value from Results.ini
        step_no = param2.split(" ")[1].split()
        rhs_val = utils.read_from_Resultfile((int(step_no[0])))
    else:
        rhs_val = param2

    if "FAIL:" in rhs_val or "FAIL:" in lhs_val:
        library.write_log(lib_constants.LOG_INFO, "INFO: Config Entry is not "
        "updated, Hence Calculation failed", tc_id, script_id, "None", "None",
        log_level, tbd)
        return "False", "None"

    if "Step-" in rhs_val or "Step-" in lhs_val:
        library.write_log(lib_constants.LOG_INFO,"INFO: Step value is not "
        "present, Hence Calculation failed", tc_id, script_id, "None", "None",
        log_level, tbd)
        return "False", "None"
    elif "MB" in lhs_val or "MB" in rhs_val:
        lhs_val = lhs_val.split("MB")[0].replace(',', '')
        rhs_val = rhs_val.split("MB")[0].replace(',', '')
    else:
        pass

    lhs = str(number_conversion(lhs_val.upper()))                               #Calling function for converting binary/hexa/decimal to int
    rhs = str(number_conversion(rhs_val.upper()))                               #Calling function for converting binary/hexa/decimal to int

    core_flag = False
    if "Core" in lhs or "CORE" in lhs or "CORE(S)" in lhs or "Cores(s)" in lhs:
        lhs = lhs.split()
        lhs = lhs[0][0]
        rhs = str(int(float(rhs)))
        core_flag = True
    else:
        pass

    if "." in lhs and "." in rhs:                                               # If number is float, taking only integer part
        lhs = lhs.split(".")[0]
        rhs = rhs.split(".")[0]
    else:
        pass

    time.sleep(lib_constants.FIVE_SECONDS)
    calculate = str(lhs) + " " + operator + " " + str(rhs)

    ###############################Calculation##################################
    try:
        if "^" == str(operator):
            result = math.pow(float(lhs), float(rhs))                           #Performing Power Operation
        elif str(operator).strip() == '<<':
            result = int(float(lhs)) << int(float(rhs))                         #Performing Bitwise Left Shift Operation
        elif str(operator).strip() == '>>':
            result = int(float(lhs)) >> int(float(rhs))                         #Performing Bitwise Right Shift Operation
        elif str(operator).strip() == '|':
            result = int(float(lhs)) | int(float(rhs))                          #Performing Bitwise OR Operation
        elif str(operator).strip() == '&':
            result = int(float(lhs)) & int(float(rhs))                          #Performing Bitwise AND Operation
        else:
            if core_flag:
                result = int(eval(str(calculate)))
            else:
                result = float(eval(str(calculate)))                            #Performing Arithmetic Operation

        return result, calculate
    except:
        return "False", "None"
###########################Global Library imports###############################
import sys
import os
import time
###########################Local Library imports################################
import library
import lib_constants
import utils
################################################################################


def binary_to_decimal(num):
    num=num.replace("'b","")
    num=int(num,2)                                                              #Converting to Decimal from Binary
    return (str(num)+"'d")

def octa_to_decimal(num):
    num=num.replace("'o","")
    num=int(num,8)                                                              #Converting to Decimal from Octa
    return (str(num)+"'d")

def hexa_to_decimal(num):
    num=num.replace("'h","")
    num=int(num,16)                                                             #Converting to Decimal from Hexa
    return (str(num)+"'d")

def decimal_to_binary(num):
    num=num.replace("'d","")
    num=bin(int(num))[2:]                                                       #Converting to Binary from Decimal
    return (str(num)+"'b")

def octa_to_binary(num):
    num=num.replace("'o","")
    num=bin(int(num, 8))[2:]                                                    #Converting to Binary from Octa
    return (str(num)+"'b")

def hexa_to_binary(num):
    num=num.replace("'h","")
    num=bin(int(num, 16))[2:]                                                   #Converting to Binary from Hexa
    return (str(num)+"'b")

def binary_to_octa(num):
    num=num.replace("'b","")
    num=oct(int(num, 2)).replace("L","")                                        #Converting to Octa from Binary
    return (str(num)+"'o")

def decimal_to_octa(num):
    num=num.replace("'d","")
    num=oct(int(num)).replace("L","")                                           #Converting to Octa from Decimal
    return (str(num)+"'o")

def hexa_to_octa(num):
    num=num.replace("'h","")
    num=oct(int(num, 16)).replace("L","")                                       #Converting to Octa from Hexa
    return (str(num)+"'o")

def binary_to_hexa(num):
    num=num.replace("'b","")
    num=hex(int(num, 2))[2:].replace("L","")                                    #Converting to Hexa from Binary
    return (str(num)+"'h")

def decimal_to_hexa(num):
    num=num.replace("'d","")
    num=hex(int(num))[2:].replace("L","")                                       #Converting to Hexa from Decimal
    return (str(num)+"'h")

def octa_to_hexa(num):
    num=num.replace("'o","")
    num=hex(int(num, 8))[2:].replace("L","")                                    #Converting to Hexa from Octa
    return (str(num)+"'h")

def log_message(original_value,result,convert_from,convert_to,test_case_id,
                script_id,loglevel,tbd):
    library.write_log(lib_constants.LOG_INFO,"INFO: Conversion Of : "+
                      str(original_value)+" From : "+str(convert_from) +
                      " To : "+str(convert_to) + " Is : "+str(result),
                      test_case_id,script_id,"none","none",loglevel,tbd)
    return result


################################################################################
# Function Name : lib_compare_step_results
# Parameters    : test_case_id ,script_id, lhs,operator,rhs,log_level,tbd
# Return Value  : Returns 1 if "PASS" and 0 if "FAIL" in comparison
# Functionality : Compares the values of step m with step n / configvar value /
#                 direct value
################################################################################

def conversion_of_numerical_format(test_case_id,script_id,ostr,loglevel,tbd):   #Function definition for converting numerical format
    token = utils.ProcessLine(ostr)
    if "CONFIG" in token[1]:                                                    #Check if token[1] is a config var and retrieve its value from config.ini
        (config, section, key) = token[1].split("-")
        original_value = utils.ReadConfig(section, key)
        convert_from = token[2].strip()
        convert_to=token[4].strip()
        if "FAIL" in original_value:
            library.write_log(lib_constants.LOG_INFO,"INFO: Config Entry is not"
                            " updated. Hence Comparision failed."
                              , test_case_id,script_id,
                              "none","none",loglevel,tbd)
            return False


    elif "STEP" in token[1]:
        step_no = token[2]
        original_value = utils.read_from_Resultfile((int(step_no)))             #token[2] is the step number. Retrieve the step # value from result.ini
        convert_from = token[3].strip()
        convert_to=token[5].strip()
        if "not present in result.ini" in original_value.lower():
            library.write_log(lib_constants.LOG_INFO,"INFO: " + str(original_value)
                              +"  Hence Comparision failed.", test_case_id,
                              script_id,"none","none",loglevel,tbd)
            return False

    else:
        original_value = token[1]                                               #if token[1] is neither a config value or a step result, consider it as the direct value for conversion.
        convert_from = token[2].strip()
        convert_to=token[4].strip()


    if "BINARY" == convert_from.upper() and "DECIMAL" == convert_to.upper():
        return log_message(original_value,binary_to_decimal(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Binary to Decimal

    elif "BINARY" == convert_from.upper() and "HEX" == convert_to.upper():
        return log_message(original_value,binary_to_hexa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Binary to Hexa

    elif "BINARY" == convert_from.upper() and "OCTA" == convert_to.upper():
        return log_message(original_value,binary_to_octa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Binary to Octa

    elif "OCTA" == convert_from.upper() and "HEX" == convert_to.upper():
        return log_message(original_value,octa_to_hexa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Octa to Hexa

    elif "OCTA" == convert_from.upper() and "BINARY" == convert_to.upper():
        return log_message(original_value,octa_to_binary(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Octa to binary

    elif "OCTA" == convert_from.upper() and "DECIMAL" == convert_to.upper():
        return log_message(original_value,octa_to_decimal(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Octa to decimal

    elif "DECIMAL" == convert_from.upper() and "BINARY" == convert_to.upper():
        return log_message(original_value,decimal_to_binary(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Decimal to Binary

    elif "DECIMAL" == convert_from.upper() and "OCTA" == convert_to.upper():
        return log_message(original_value,decimal_to_octa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Decimal to Octa

    elif "DECIMAL" == convert_from.upper() and "HEX" == convert_to.upper():
        return log_message(original_value,decimal_to_hexa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Decimal to Hexa

    elif "HEX" == convert_from.upper() and "BINARY" == convert_to.upper():
        return log_message(original_value,hexa_to_binary(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Hexa to Binary

    elif "HEX" == convert_from.upper() and "OCTA" == convert_to.upper():
        return log_message(original_value,hexa_to_octa(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Hexa to Octa

    elif "HEX" == convert_from.upper() and "DECIMAL" == convert_to.upper():
        return log_message(original_value,hexa_to_decimal(original_value),
                convert_from,convert_to,test_case_id,script_id,loglevel,tbd)    #Conversion From Hexa to Decimal

    else:
        return False
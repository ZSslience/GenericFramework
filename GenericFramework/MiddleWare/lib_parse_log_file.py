__author__ = r"bchowdhx\skotasiv\tnaidux"

# General Python Imports
import codecs
import fnmatch
import os
import re
import chardet

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : quote_string
# Parameters    : parameter - string to search  
# Functionality : Parsing log
# Return Value  : 'True'on successful action and 'False' on failure
################################################################################


def quote_string(input_string, file_path, test_case_id, script_id,
                 log_level="ALL", tbd=None):
    
    input_string = input_string.upper()
    token, pos = utils.extract_parameter_from_token(input_string.split(), 
                                                    "FOR", "FROM")              # Extracting the string to search
    search_string = token
    
    if "UNDER" in search_string:                                                # Check for log section mentioned in the step
        log_section = search_string.split("UNDER")[1].strip()
    
    library.write_log(lib_constants.LOG_INFO, "INFO: Searching for '%s' in "
                      "file %s" % (search_string, file_path), test_case_id, 
                      script_id, "None", "None", log_level, tbd)
    
    if "'" in search_string:
        search_string = search_string.replace("'", "")                          # Replacing single qoute from search string
    
    if "config-" in search_string.lower():
        original_search_string = \
            utils.configtagvariable(search_string.strip(" "))
    else:
        original_search_string = search_string

    search_string = remove_spaces(original_search_string)                       # Remove spaces in the string

    temp_file = "temp.txt"                                                      # Create a temp file to print log in reverse manner
    script_dir = lib_constants.SCRIPTDIR
    log_path = script_dir + "\\" + temp_file
    
    with open(file_path) as f,  open(log_path, 'w') as f1:
        f1.writelines(reversed(f.readlines()))                                  # Print content in reverse order to temp file
        f1.close()

    if "LOWPOWER" in search_string.upper():
        start = search_string.find("(")
        end = search_string.find(")")
        value = search_string[start:end]
        value = value.strip("(")
        with codecs.open(file_path, "r", "utf-8") as f:
            for line in f:
                line = remove_spaces(line)
                if value.upper().strip() in line.upper().strip():               # If log section is found
                    return True, value.strip()                                  # From here search for the actual string
                else:
                    continue
        return False, False
    elif "UNDER" in search_string.upper():                                      # To search string under a log section in the log
        search_for = search_string.split("UNDER")[0].strip()
        search_string = log_section                                             # log file used as it is without reversing
        search_string = remove_spaces(search_string)
        with codecs.open(file_path, "r", "utf-8") as f:
            try:
                for line in f:
                    line = remove_spaces(line)
                    if search_string.upper().strip() in line.upper().strip():   # If log section is found
                        if log_section.upper().strip() in \
                                search_string.upper().strip():
                            search_string = search_for                          # From here search for the actual string
                        else:
                            return True, line.strip()
                    else:
                        continue
            except Exception as e:
                print("#######################################################")
                print(e)
                with codecs.open(file_path, "r",
                                 encoding='unicode_escape') as f:
                    for line in f:
                        line = remove_spaces(line)
                        if search_string.upper().strip() in \
                                line.upper().strip():                           # If log section is found
                            if log_section.upper().strip() in \
                                    search_string.upper().strip():
                                search_string = search_for                      # From here search for the actual string
                            else:
                                return True, line.strip()
                        else:
                            continue
        return False, False
    elif "SPEED" in search_string.upper():
        search_string = "Memory Frequency"
        with codecs.open(file_path, "r", "utf-8") as f:
            for line in f:
                if search_string.upper().strip() in line.upper().strip():       # If log section is found
                    val = line.split(":")[1]                                    # From here search for the actual string
                    val = val.split()[0]
                    return True, val.strip()
                else:
                    continue
        return False, False
    else:
        if "MEMORYINITCOMPLETE" in search_string or \
                "ENDOFDXEPHASE" in search_string or \
                "BIOSBOOTCOMPLETE" in search_string:
            with codecs.open(file_path, "r", "utf-8") as f:
                for line in f:
                    if "Type=222" in line and "Handle" in line:
                        values = []
                        for data in f:
                            if "*" in data:
                                data_line = str(data)
                                data_line = data_line.split("*")
                                data_list = data_line[1]
                                values.append(data_list)
                            else:
                                return False
                        data_list = "".join(values)
                        item = data_list.replace(".", " ")
                        search_found = item.strip()
                        search_found = search_found.strip(" 0")
                        search_found = remove_spaces(search_found)
                        search_found = search_found.upper()
            if search_string in search_found:
                return True, search_found
            else:
                return False

    file_enc = determine_encoding_of_file(file_path, test_case_id, script_id,
                                          log_level, tbd)

    try:
        with codecs.open(file_path, "r", file_enc) as f:                        # Open the reversed log file for searching in utf-8
            for line in f:
                line = remove_spaces(line)                                      # Removes spaces from the lhs and rhs strings
                if search_string.upper().strip() in line.upper().strip():
                    if ":" in line and 'SPIBAR' in line.upper():
                        return True, (line.split(':')[1]).strip() + 'h'
                    elif ":" in line and "=" in search_string:
                        search_split = search_string.split("=")
                        if search_split[0] in line.upper() and \
                           search_split[1] in line.upper():
                            return True, line.strip()
                    elif ":" in line and "EDX" in line.upper():
                        temp = line.split(":")[-1].strip() + "'h"
                        return True, temp
                    elif ":" in line:
                        if "PHYSICALPROCESSORCORES" in line.upper():
                            temp = line.split(":")[-1].strip() + "core(s)"
                            return True, temp
                        elif "LOGICALPROCESSORCORES" in line.upper():
                            temp = line.split(":")[-1].strip() + "thread(s)"
                            return True, temp
                        else:
                            return True, (line.split(':')[-1]).strip()
                    elif "BIOSVERSION" in line.upper():
                        return True, line.strip()
                    else:
                        if "PMCFWVERSION" in line.upper():
                            for constant in range(lib_constants.THREE):         # Iterating to the next 3 lines
                                line = next(f)
                                if "FW VERSION" in line.upper():                # If fw version in line
                                    temp = re.sub("\D", ".", line).strip('.')   # Extracting fw version form line
                            return True, temp
                        elif "FWVERSION" in line.upper() and \
                                        "PMCFWVERSION" not in line.upper():
                            temp = re.sub("\D", ".", line).strip('.')
                            return True, temp
                        else:
                            if '0x' in line:
                                return True, line.strip()
                            elif line.isalnum() in line:
                                return True, line.strip()
                            else:
                                return True, line.strip()
                else:
                    continue
        return False, False
    except:
        with codecs.open(file_path, 'r', "windows-1252") as f:                  # Windows-1252 encoding, if exception in utf-8
            for line in f:
                la = ''                                                         # Remove spaces in the lhs and rhs strings
                ls = ''
                lg = ''
                ls = re.split('\x00 |\x00', line)                               # Remove junk characters
                la = la.join(ls)
                line = la
                ls = line.split('\t')
                lg = lg.join(ls)
                line = lg
                if (original_search_string.upper().strip() in 
                        line.upper().strip()) or \
                   (search_string.upper().strip() in line.upper().strip()):
                    if ":" in line and 'SPIBAR' in line.upper():                # Efi command for SPIBAR returns value as hex
                        return True, (line.split(':')[1]).strip() + 'h'
                    elif ":" in line:
                        return True, (line.split(':')[1]).strip()

                    else:
                        return True, line.strip()

                elif ":" in search_string and \
                        (search_string.replace(" ", "").upper() in
                         line.replace(" ", "").upper()):
                    return True, line.strip()
                else:
                    continue
        return False, False

################################################################################
# Function Name : lib_parse_log_file
# Parameters    : parameter - string to search, delimeter - symbols, 
#                 expected - expected string, source- log path
# Functionality : Parsing log
# Return Value  : 'True'on successful action and 'False' on failure
################################################################################


def lib_parse_log_file(token, test_case_id, script_id, log_level="ALL", 
                       tbd="None"):

    try:
        global extracted_step, file_path
        token = token.upper()                                                   # Convert to upper case
        source = token.rsplit("FROM", 1)                                        # Split string token with "FROM" only 1 time
        extracted_operation = source[0].strip()
        extracted_source = source[1].strip()                                    # Store the 2nd element in source which is the source

        if "CONFIG-" in extracted_source.upper():                               # To bypass operation on config related syntax
            pass
        else:
            extracted_source_nospace = extracted_source.split(" ")
            extracted_step = extracted_source_nospace[1]                        # Extract step number from extracted source

        extracted_operation = extracted_operation.split("FOR", 1)               # Split with "FOR" 1 time
        parameters = extracted_operation[1].strip()                             # Extract the operation to perform
        equal_flag = False

        if "CONFIG-" in source[1]:
            file_path = utils.configtagvariable(extracted_source)               # Extract file_path from config file
        else:
            file_path = utils.read_from_Resultfile(extracted_step)              # Extract file path from config file

        if file_path.find('PTTBAT') != -1:                                      # For PTTBBAT tool logs
            log_path = file_path.split('$')[0]                                  # Read path and test name from result file
            test_name = file_path.split('$')[1]
            ptt_log_path = lib_constants.PTTBATPATH
            try:
                new_log_path = os.path.join(ptt_log_path,
                                            os.listdir(ptt_log_path)[0])
                file_list = fnmatch.filter(os.listdir(new_log_path),
                                           '*' + (test_name) + '_PASS.txt')
                file_name = file_list[0]
                file_path = os.path.join(ptt_log_path, new_log_path, file_name)
                if not file_list:                                               # Check if the log file is present in the path
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "The log file %s is not found, command "
                                      "run have failed" % file_path,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False, 0
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)

        if "FAIL" == file_path.upper():                                         # If previous step is failing then this code will return False and exit
            return False, 0
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: The file to "
                              "parse is %s" % file_path, test_case_id,
                              script_id, "None", "None", log_level, tbd)

        if "=" in parameters:
            first_part_of_param = parameters.split("=")[0].strip()              # Split first part of param with = and store it after stripping white spaces
            equal_flag = True

        if "CONFIG-" in parameters:
            if "'" in parameters:
                parameters = parameters.strip("'")
                parameters = utils.configtagvariable(parameters)                # Extract operation from config file
            else:
                parameters = utils.configtagvariable(parameters)

            if equal_flag:
                parameters = first_part_of_param + "=" + parameters             # Get the original string with the value after extracting it from config file

        if "NONE" in parameters.upper():
            str = open(file_path, 'r').read()
            return True, str
        else:
            parameters = parameters

        mt = re.search(r'[|[|]|]', parameters)

        if 'PCR' in parameters.upper() and mt == None:                          # PCR PCRDUMP logs, not TBS
            if 'PCRDUMP64' in open(file_path).read():
                library.write_log(lib_constants.LOG_INFO, "INFO: Reading "
                                  "PCRDUMP.efi logs", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                status, result = parse_pcrdumpefi_log(parameters, file_path,
                                                      test_case_id, script_id)
        elif 'TBS' in open(file_path).readline():
            status, result = parse_tbs_sipachk_log(parameters, file_path,
                                                   test_case_id, script_id)
        else:
            status, result = quote_string(token, file_path, test_case_id,
                                          script_id, log_level, tbd)

        if "NONE" == status:
            return False, result
        elif status:
            return True, result
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Searching for "
                              "%s in file %s" % (parameters, file_path),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            action, value = \
                check_action(token, parameters, file_path, test_case_id,
                             script_id, log_level, tbd)                         # Call to check action required to perform
            if action:
                return True, value
            else:
                return False, value
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : check_action
# Parameters    : token, parameters, file_path, test_case_id, script_id,
#                 log_level and tbd
# Purpose       : Parsing log
# Return Value  : value and true on successful action and 'False' on failure
################################################################################


def check_action(token, parameters, file_path, test_case_id, script_id,
                 log_level="ALL", tbd="None"):

    try:
        original_string = token
        single_quote_pattern = re.compile(r"\'(.+?)\'")                         # Pattern to check for quote in token
        double_quote_pattern = re.compile(r"\"(.+?)\"")
        single_quote = re.search(single_quote_pattern, original_string)         # Searches for the given pattern and returns an object
        double_quote = re.search(double_quote_pattern, original_string)         # Searches for the given pattern and returns an object

        if single_quote is not None or double_quote is not None:                # If search is successfull keep quote "True" else "False"
            quote = True
            op_remove_quote = re.findall(r"'(.*?)'", parameters, re.DOTALL)     # Remove quoutes from the string
            parameters = op_remove_quote[0]                                     # Choose the first element from the list as the opearation to perform
        else:
            quote = False                                                       # Put quote as false

        result, value = parse_log(token, parameters, file_path, quote,
                                  test_case_id, script_id, log_level, tbd)      # Call function with the updated operation and file path
        if result is not None or result is not False:                           # If result is not None or false return result and value
            return result, value
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : parse_log
# Parameters    : token, parameters, file_path, quote, test_case_id, script_id,
#                 log_level and tbd
# Purpose       : Parsing log
# Return Value  : True on successful action, False otherwise
################################################################################


def parse_log(token, parameters, file_path, quoute, test_case_id, script_id,
              log_level="ALL", tbd="None"):                                     # File reading and string search logic

    try:
        global ret_val, count_new

        if quoute:                                                              # If quotes variable is true do the following
            if "=" in token:                                                    # If = is there after quoutes
                res_token = token.split("=")
                extracted_token = res_token[1].strip()                          # Remove white spaces from left and right side of the string
                extracted_token = extracted_token.split(" ")                    # Split with " "
                result = extracted_token[0]                                     # Capture the first element of the list in super_new variable
                with codecs.open(file_path, "r", "utf-8") as handler:           # Open the file using codecs in utf-8 format
                    for line in handler:                                        # Iterate through the file
                        if parameters in line.upper():                          # Check for required line
                            if result in line.upper():                          # Check for value after = after quoutes string
                                return True, result                             # Return true and value after quoutes to be matched
                            else:
                                pass
                        else:
                            pass
            else:                                                               # Quotes without = after quotes
                value = 0
                with codecs.open(file_path, "r", "utf-8") as handler:           # Open the file using codecs in utf-8 format
                    for line in handler:                                        # Iterate through the file
                        if parameters in line.upper():                          # Search for operation in line
                            value = 1                                           # Return True and return string Found
                        else:
                            pass
                if 1 == value:
                    return True, "Pass"
                else:
                    return False, "Fail"
        else:                                                                   # When quoute is not there
            if "__" in parameters:
                newop = parameters.split("__")                                  # Splitting the new string with "__"
                value_to_check = newop[1]                                       # 2nd element is value to check
                value_to_find = newop[0]                                        # 1st element is value to find

                with codecs.open(file_path, "r", "utf-8") as handler:           # File operation using codecs
                    for line in handler:                                        # Iterate through lines
                        line = line.strip()                                     # Strip the white spaces
                        if value_to_check in line.upper():                      # Check for value to check in line
                            if value_to_find.upper() in line:                   # Ifelse added just for output messages implementation
                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: %s is present in log"
                                                  % value_to_check,
                                                  test_case_id, script_id,
                                                  "None", "None", log_level,
                                                  tbd)
                                return True, "Pass"
                            else:
                                pass
                        else:
                            pass

            temp_file = "temp.txt"                                              # Create a temp file to print log in reverse manner
            script_dir = lib_constants.SCRIPTDIR
            log_path = script_dir + "\\" + temp_file

            with open(file_path) as f, open(log_path, 'w') as f1:
                f1.writelines(reversed(f.readlines()))                          # Print content in reverse order to temp file
                f1.close()

            file_enc = determine_encoding_of_file(log_path, test_case_id,
                                                  script_id, log_level, tbd)

            with codecs.open(log_path, "r", "utf-16-le") as handler:            # Open the file using codecs in utf-8 format
                ret_val = 0
                for line in handler:                                            # Iterate through the file
                    line = line.strip()                                         # Strip spaces from both sides
                    line = remove_spaces(line)
                    line = line.replace(":", "")
                    parameters = remove_spaces(parameters)
                    parameters = parameters.replace(":", "")
                    if parameters.upper() in line.upper():                      # Search for string in line
                        ret_val = 1
                        count_new = line.upper()
                        break
                    else:
                        pass

            if 1 == ret_val:
                new_part = count_new.split(parameters.upper())[1]
                return True, new_part
            elif 0 == ret_val:
                return False, "Fail"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : parse_pcrdumpefi_log
# Parameters    : parameters, file_path, test_case_id, script_id, log_level and
#                 tbd
# Purpose       : Parsing pcrdump.efi tool log for PCR values
# Return Value  : True & result on successful action and False & result on
#                 failure
################################################################################


def parse_pcrdumpefi_log(parameters, file_path, test_case_id, script_id,
                         log_level="ALL", tbd="None"):

    try:
        with open(file_path, mode="r") as source:                               # Open and read the log file
            result = ''
            found = False
            for line in source.readlines():
                if parameters in line:                                          # 1st line of the PCR value
                    line1 = line
                    l1 = line1.split(' ')
                    lj = ''
                    for item in line1:
                        if item != ' ':
                            lj = lj + str(item)                                 # Remove spaces
                        else:
                            pass
                    found = True
                    result = str(lj).split(':')[1]
                elif True == found and 'PCR' not in line:                       # 2nd line of the PCR value
                    line2 = line
                    l2 = line2.split(' ')
                    lj2 = ''
                    for item in line2:
                        if item != ' ':
                            lj2 = lj2 + str(item)                               # Remove spaces
                        else:
                            pass
                    found = False
                    str1 = str(lj) + str(lj2)                                   # Combine the 2 lines
                    result = str1.replace("\n", "")                             # Remove the \n
                    result = result.split(":")[1]
                    break
                else:
                    if True == found:
                        break
                    else:
                        pass

            if result == '':
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to parse log for PCRDUMP tool logs",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False, None
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Parse log "
                                  "for PCRDUMP tool logs successful",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True, result
        source.close()
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : remove_spaces
# Parameters    : Input to remove spaces, output without spaces
# Purpose       : To remove spaces from a given line in a file
# Return Value  : Output string with spaces between words removed
################################################################################


def remove_spaces(input_line):

    ls = ''                                                                     # Removes spaces between the words in the log
    la = ''
    ls = input_line.split(' ')                                                  # Split the line into words by spaces
    la = la.join(ls)                                                            # Join all the words
    return la

################################################################################
# Function Name : parse_tbs_sipachk_log
# Parameters    : parameters, file_path, test_case_id, script_id, log_level and
#                 tbd
# Purpose       : Parsing tbslog or sipachk log for PCR values
# Return Value  : True & result on successful action, False & result on failure
################################################################################


def parse_tbs_sipachk_log(parameters, file_path, test_case_id, script_id,
                          log_level="ALL", tbd="None"):

    try:
        new_log = lib_constants.SCRIPTDIR + '\\tbs_sipachk.log'
        if os.path.isfile(new_log):
            os.remove(new_log)

        with open(file_path, mode="r") as source, open(new_log, "a") as new1:
            lines = source.read().splitlines()
            for line in lines[-25:-1]:
                new1.writelines(line + "\n")
            new1.close()

        parameters = remove_spaces(parameters)

        with open(new_log, mode="r") as f:
            for line in f.readlines():
                line = remove_spaces(line)
                if parameters.lower().strip() in line.lower().strip():
                    return True,line.strip()
                else:
                    continue
            return "NONE", False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def determine_encoding_of_file(file_path, test_case_id, script_id, loglevel,
                               tbd=None):

    try:
        if file_path is None:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the path of a file created", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return False
        else:
            rawdata = open(file_path, "r").read()
            result = chardet.detect(bytearray(rawdata, encoding="utf8"))
            char_coding = result['encoding']
            return char_coding
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False

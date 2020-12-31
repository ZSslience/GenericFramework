__author__ = "Automation Development Team"

# General Python Imports
import os

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : verify_place_of_occurrence
# Parameters    : token, test_case_id, script_id, log_level, tbd
# Functionality : Calculate string occurrence
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def verify_place_of_occurrence(token, test_case_id, script_id, log_level="ALL",
                               tbd="None"):

    try:
        tokenlist = []
        tokenlist = token.split(" ")                                            # Split tokenlist with space
        token = []

        for i in range (len(tokenlist)):                                        # Iterate through the tokenlist
            if str(tokenlist[i]).startswith("'") or \
               str(tokenlist[i]).endswith("'"):
                tokenlist[i] = str(tokenlist[i]).replace("'","")                # Replace single quoute
            token.append(tokenlist[i])                                          # Append to list the replaced string

        logpath = utils.read_from_Resultfile(str(token[-2]))                    # Store the logpath from Result file

        token = " ".join(token)
        if 'AFTER' in token.upper() or 'BEFORE' in token.upper():               # check for string "AFTER" or "BEFORE"
            stringlist1 = []
            token = token.split(" ")
            for pos in range(len(token)):                                      # Iterate through the token
                if 'AFTER' == token[pos] or 'BEFORE' == token[pos]:
                    positionafter = pos-1                                       # Store the position of the string

            for item in token[2:positionafter]:                                 # Iterate through the item after the occurance
                stringlist1.append(item)

            stringtosearch_1 = " ".join(stringlist1)                            # Join with space
            stringlist2 = []

            for pos in range(len(token)):
                if 'FROM' == token[pos]:                                        # Check for position of From
                    positionfrom = pos

            for item in token[positionafter+2:positionfrom]:
                stringlist2.append(item)
            stringtosearch_2 = " ".join(stringlist2)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Grammar "
                              "syntax is wrong", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        result = string_comparison(stringtosearch_1, stringtosearch_2, logpath,
                                   test_case_id, script_id, token, log_level,
                                   tbd)

        if result:
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id,  "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : string comparison
# Parameters    : stringtosearch_1, stringtosearch_2, logpath, test_case_id,
#                 script_id, token, log_level, tbd
# Functionality : string position comparison
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def string_comparison(stringtosearch_1, stringtosearch_2, logpath, test_case_id,
                      script_id, token, log_level="ALL", tbd="None"):

    try:
        path = logpath
        log = open(path, 'r').read()                                            # Open the file and perform read
        text = log                                                              # Store in text
        sub_list_1 = []
        sub_list_2 = []
        sub_str_1 = ""
        sub_str_2 = ""

        for f in text:                                                          # Iterate through the text
            text = text.replace(f, f.lower())

        if os.path.exists(path):                                                # If path to log exists
            if stringtosearch_1.lower() in text:                                # If stringtosearch in text
                result = comparison_func(stringtosearch_1, stringtosearch_2,
                                         path, text, test_case_id, script_id,
                                         token, log_level, tbd)

                if result:
                    return True
                else:
                    return False
            elif '[HECI1]' in stringtosearch_1:
                if '90000255)' in stringtosearch_1:
                    n = 5
                else:
                    n = 4

                list_to_search = stringtosearch_1.split()
                inc = 0

                for item in list_to_search:
                    inc += 1
                    if inc <= n:
                        sub_list_1.append(item)
                    else:
                        sub_list_2.append(item)

                sub_str_1 = ','.join(sub_list_1)
                sub_str_1 = sub_str_1.replace(',', ' ')
                sub_str_2 = ','.join(sub_list_2)
                sub_str_2 = sub_str_2.replace(',', ' ')

                result_1 = comparison_func(sub_str_1, stringtosearch_2, path,
                                           text, test_case_id, script_id,
                                           token, log_level, tbd)

                result_2 = comparison_func(sub_str_2, stringtosearch_2, path,
                                           text, test_case_id, script_id,
                                           token, log_level, tbd)

                if result_1 and result_2:
                    return True
                else:
                    return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Logfile "
                              "not found", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id,  "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : comparison_func
# Parameters    : stringtosearch_1, stringtosearch_2, logpath, text,
#                 test_case_id, script_id, token, log_level, tbd
# Functionality : string position comparison
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def comparison_func(stringtosearch_1, stringtosearch_2, path, text,
                    test_case_id, script_id, token, log_level="ALL",
                    tbd="None"):

    try:
        if stringtosearch_1.lower() in text:                                    # If stringtosearch in text
            if stringtosearch_2.lower() in text:
                if 'AFTER' in token:                                            # If AFTER in token
                    if (int(text.index(stringtosearch_1.lower()))) > \
                       (int(text.index(stringtosearch_2.lower()))):             # Index of first string > index of 2nd string
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "string %s occurs after %s in the "
                                          "file %s" % (stringtosearch_1,
                                                       stringtosearch_2, path),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " string %s does not occur after %s "
                                          "in the file %s" % (stringtosearch_1,
                                                              stringtosearch_2,
                                                              path),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
                elif 'BEFORE' in token:                                         # If index of first string is < index of 2nd string
                    if (int(text.index(stringtosearch_1.lower()))) < \
                       (int(text.index(stringtosearch_2.lower()))):
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "string %s occurs before %s in the "
                                          "file %s" % (stringtosearch_1,
                                                       stringtosearch_2, path),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          "string %s does not occur before "
                                          "%s in the file %s"
                                          % (stringtosearch_1,
                                             stringtosearch_2, path),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
                else:
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                  "Comparison string %s not found in logfile"
                                  % stringtosearch_2, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Comparison "
                              "string %s not found in logfile"
                              % stringtosearch_1, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return False

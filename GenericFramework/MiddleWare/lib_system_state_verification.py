__author__ = "jkmody\kapilshx"

#########################General library imports################################
import os
import glob
import string
###############################################################################
#########################Local library imports##################################
import library
import lib_constants
import utils
################################################################################

################################################################################
#  Function     : verify_system_state
#  Description  : Verify cstate values from log file and input syntax
#  Param        : token, testcase id, script id, loglevel and tbd
#  Purpose      : package residency parsing for ALL and other cores
#  Return       : returns dictionary of available cpu's and cpu name
################################################################################


def verify_system_state(token, test_case_id, script_id, loglevel="ALL",
                  tbd="None"):

    if "CONFIG" in token.upper():
        temp_list = token.split()
        config_entry = temp_list[-1]
        value = utils.ConfigTagVariable(config_entry)
        token = token.replace(value, config_entry)
    else:
        pass

    if "PACKAGE" in token.upper():                                              #if "PACKAGE" is present in the token
        result, cpu_name = package_residency(token, test_case_id, script_id,
                                 loglevel, tbd)
        if False == result:                                                     #if CPU core is not found in the log file
            library.write_log(lib_constants.LOG_INFO, "INFO: The CPU core is "
                    "not found in log file", test_case_id, script_id,
                              "SocWatch_tool","None", loglevel, tbd)
            return False
        for x,y in result.iteritems():                                          #trying to iterate the c-states and their core percentage in the log file
            library.write_log(lib_constants.LOG_INFO, "The value of package %s "
                "in log is %s"%(x,y), test_case_id, script_id, "SocWatch_tool",
                              "None",loglevel, tbd)
        token_list = token.split()                                              #convert to list
        if "%" in token_list[5]:                                                #if percent(%) is present in the token
            token_list_perc = token_list[5].split('%')[0]
            data = float(token_list_perc)-10
        else:                                                                   #if percent(%) is not present in the token
            data = token_list[5]
            data = float(data)-10                                                 #extract the value to compare with
        operator = token_list[4]                                                #extract the operator
        detect_flag, pass_counter, result_flag_counter = False, 0, 0            #initializing the parameter

        if "ALL" in token.upper():                                              #if ALL in token
            package_all = 0
            for key in result:                                                  #iterate through the result dict
                pass_counter += 1
                value_dict = result[key]                                        #store the value of key from dict
                value_dict = float(value_dict.split('%')[0] )                   #remove the percentage
                package_all +=value_dict
            result_flag = compare_values(package_all, data, operator,
                                   test_case_id, script_id, loglevel, tbd)  #function call to compare the results
            if result_flag:
              detect_flag = True                                            #comparison successful
            else:
              detect_flag = False                                           #comparison failed
        else:
            for key in result:                                                  #iterate through the result dictionary
                if key == cpu_name:                                             #if key matches with the core name
                    value_dict = result[key]
                    value_dict = float(value_dict.split('%')[0])                #remove the percentage sign
                    result_flag = compare_values(value_dict, data, operator,
                                        test_case_id, script_id, loglevel, tbd) #function call to compare the results
                    if result_flag:
                       detect_flag = True
                       result_flag_counter += 1
                    else:
                       detect_flag = False
                else:
                    pass

        if detect_flag :                                                        #if result of comparison  for package residency is true
            library.write_log(lib_constants.LOG_INFO, "Verified successfully "
                "c-state for %s %s %s"%(token_list[3], operator, data ),
                test_case_id, script_id, "SocWatch_tool", "None",loglevel, tbd)
            return True
        else:                                                                   #if result of comparison  for package residency is not true
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to verify "
                    "c-state for %s %s %s"%(token_list[3], operator, data ),
                test_case_id, script_id, "SocWatch_tool", "None", loglevel, tbd)
            return False

    elif "CORE" in token.upper():                                               #if CORE in token
        result, cpu_name = core_residency(token, test_case_id, script_id,
                                          loglevel, tbd)                        #call function to get dictionary of values and cpu name to parse
        cpu_number_token = ((token.split(' ')[3]).split('_')[0])[-1]
        if False == result:                                                     #if CPU core is not found in the log file
            library.write_log(lib_constants.LOG_INFO, "INFO: The CPU core is "
                "is not found in log", test_case_id, script_id, "SocWatch_tool",
                              "None",loglevel, tbd)
            return False
        for x,y in result.iteritems():                                          #trying to iterate the c-states and their core percentage in the log file
            if not str(cpu_number_token).isdigit():                             #if core is given like  - core_ALL
                library.write_log(lib_constants.LOG_INFO, "The value of %s "
                "in log is %s"%(x,y), test_case_id, script_id, "SocWatch_tool",
                                  "None", loglevel, tbd)
            else:                                                               #if core is not core_ALL it should be like  - core_1 or core_2
                library.write_log(lib_constants.LOG_INFO, "The value of "
                    "core%s_%s in log is %s"%(cpu_number_token,x,y),
                test_case_id,script_id, "SocWatch_tool","None", loglevel, tbd)
        token_list = token.split()
        if "%" in token_list[5]:                                                #if percent(%) is present in the token
            token_list_perc = token_list[5].split('%')[0]
            data = float(token_list_perc)
        else:                                                                   #if percent(%) is not present in the token
            data = token_list[5]
            data = float(data)
        operator = token_list[4]                                                #extract the operator
        detect_flag, pass_counter, result_flag_counter = False, 0, 0

        if "ALL" in token.upper():                                              #check for ALL in the token
            for key in result:                                                  #iterate through result dict
                pass_counter += 1
                value_dict = result[key]                                        #get the result from the key in dictionary
                value_dict = float(value_dict.split('%')[0])                    #remove the percentage from the value and convert the value to float
                result_flag = compare_values(value_dict, data, operator,
                                        test_case_id, script_id, loglevel, tbd) #function call to compare the values
                if result_flag:
                  result_flag_counter += 1
                else:
                  detect_flag = False
                if result_flag_counter == pass_counter:
                  detect_flag = True                                            #successful comparison
                else:
                  detect_flag = False                                           #unsuccessful comparison
        else:
            for key in result:
                value_dict = float(result[key].split('%')[0])               #convert the value to float
                result_flag = compare_values(value_dict, data, operator,
                                    test_case_id, script_id, loglevel, tbd) #function call to compare the results
                if result_flag:                                             #if True is returned change flag to 1
                   detect_flag = True                                       #successful comparison
                else:
                   detect_flag = False                                      #unsuccessful comparison

        if detect_flag:                                                         #if flag is greater than 0 (for ALL condition flag can be more than 1)
            library.write_log(lib_constants.LOG_INFO, "INFO: Verified "
            "successfully c-state for %s %s %s"%(token_list[3], operator, data ),
                test_case_id, script_id, "SocWatch_tool", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to verify "
            "c-state for %s %s %s"%(token_list[3], operator, data),
                test_case_id, script_id, "SocWatch_tool", "None", loglevel, tbd)
            return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Invalid Parameter."
                ,test_case_id, script_id, "SocWatch_tool", "None",
                          loglevel, tbd)
        utils.generate_syntaxHandlerError(test_case_id, script_id, token)
################################################################################
#  Function     : core_residency
#  Description  : get core residency values from the log file
#  Param        : token, testcase id, script id, loglevel, tbd
#  Purpose      : Finds the required values from the csv file
#  Return       : Return True if no difference found after comparing two files
################################################################################
def core_residency(token, test_case_id, script_id, loglevel="ALL", tbd="None"):
    log_file = []
    os.chdir(lib_constants.SCRIPTDIR)
    list_token = token.split()                                                  #convert to list
    core_number = list_token[3].split("_")[0]                                   #extract the required string
    core_number = core_number.lower()
    req_token = list_token[3]                                                   #get the req token[Core1_c3]
    cpu_num = req_token.split("_")[1].strip(" ")
    log_file = glob.glob("*_SOC_LOG.csv")                                   #search for the file ending with _SOC_LOG.csv which will be the file to parse
                                                                #stores the file name

    log_file.sort(key=os.path.getmtime)

    if [] == log_file:                                                          #checks if file is present in the script directory
        library.write_log(lib_constants.LOG_WARNING, "Warning: File "
        "for C-State is not present or empty.", test_case_id, script_id,
                          "SocWatch_tool","None",loglevel, tbd)
        return False, ""
    else:
        log_file=log_file[-1]
    filein = open(log_file, "r")                                                #open the file
    stream = filein.readlines()                                                 #read and store the contents in stream
    filein.close()                                                              #close the file
    c_state_flag = False
    for index, line in enumerate(stream):                                       #enumerate through the stream (contents of the log file)
        if line.startswith("Core Residency"):                                   #search for Core Residency in the line
            break                                                               #store the line number and the content
    index += 3
    core_line_num_first = index

    core_list = []
    core_line_num_last=index-1
    core_details = stream[core_line_num_last].split(",")                        #store the core details in the list
    for n, ln in enumerate(core_details):                                       #enumerate through the core and store line number and present core names in the generated log
        if '%' in ln:
            core_list.append(ln.split('(')[0].strip(' '))                       #store the first value from the list 'Core0'

    core_residency_all = {}
    cpu_num_core_data = []
    str_array = []
    row_data = 0
    core_line_num_last = index
    for core_num in range(len(core_list)):
        cpu_num_core_data.append([])
        while -1 == stream[core_line_num_last].find("-"):                       #iterate till - observed in line
            str_array = stream[core_line_num_last].split(",")                   #store the values in a list
            core_residency_all[str_array[0].strip()+"_in_"+core_list[core_num]]\
                = str_array[core_num+1].strip()
            cpu_num_core_data[row_data].append(str_array[core_num+1].strip())
            core_line_num_last+=1
        row_data+=1
        core_line_num_last = index

    c_state_value = []
    c_state_array = []
    while(1):                                                                   #iterate till - is found in the file after core residency line
        c_state_array = stream[core_line_num_first].split(",")                  #split the stream with (,) comma
        c_state_value.append(c_state_array[0].strip())                          #append the core names [c1,c2,c3,c4...]values in the list
        core_line_num_first+= 1
        if "*" in stream[core_line_num_first].split(",")[0].strip(" "):         #if '*' present in the line
            break

    if "ALL" not in req_token.upper():                                          #to check proper input of cpu_num is given
        cpu_num_flag = False
        for cpu_index,item in enumerate(c_state_value):                         #loop to cpu_num is present in c-state_value list
            if cpu_num in item.upper().strip():
                cpu_num_index = cpu_index
                cpu_num_flag = True
            else:
                pass
        if True == cpu_num_flag:                                                #if c-state value given in syntax is correct as compare to log file
            library.write_log(lib_constants.LOG_INFO, "INFO: C-state value "
                "given in syntax is correct", test_case_id, script_id,
                              "SocWatch_tool","None",loglevel, tbd)
            pass
        else:                                                                   #if failed to get the c-state value in the log file
            library.write_log(lib_constants.LOG_INFO, "INFO: C-state value "
                "given in syntax is not correct", test_case_id, script_id,
                "SocWatch_tool", "None",loglevel, tbd)
            return False,cpu_num

    if 5 == len(core_number):                                                   # for individual one value reading #code for the specific [cpu_num][core_numbre] -- [row][column] is given
        for n, ln in enumerate(core_list):                                      #enumerate through core list
            core_number_flag = 0
            if core_number in ln.lower():                                       #if core number in line
                core_number_flag = 1
                str_array_value = int(core_number[4:])+1                        #store the number of instance of the required core in the log file, it can be more than 1
                break
        if 0 == core_number_flag:                                               #if CPU core value given in sysntax is not correct as compare to log file
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG: CPU core value"
                " given in syntax is not correct", test_case_id, script_id,
                "SocWatch_tool", "None",loglevel, tbd)
            return False, cpu_num
        else:                                                                   #if CPU core value given in sysntax is correct as compare to log file
            library.write_log(lib_constants.LOG_INFO, "INFO: CPU core value"
                "given in syntax is correct", test_case_id, script_id,
                "SocWatch_tool", "None",loglevel, tbd)
            pass
    else:
        pass

    if "ALL" in req_token.upper():                                              #check for ALL in the required token string
        if 4 == len(core_number):                                               # for all data in 20 entries row and column both reading
            return core_residency_all,cpu_num
        elif 5 == len(core_number):                                             # for individual core column reading
            core_residency = {}
            cpu_num = ""                                                        #initialise empty string to cpu_name
            for index_value,item in enumerate(c_state_value):
                core_residency[item] =\
                    cpu_num_core_data[int(core_number[4:])][index_value]
            return core_residency, cpu_num
        else:                                                                   #if input syntax is incorrect
            library.write_log(lib_constants.LOG_INFO, "INFO: Input"
                " syntax is not correct", test_case_id, script_id,
                              "SocWatch_tool", "None",loglevel, tbd)
            return False,cpu_num
    else:
        if 4 == len(core_number):                                               # for individual cpu num row reading
            core_residency = {}
            for index_value in range(len(core_list)):                           #loop for core_num
                core_residency[core_list[index_value]+"_"+cpu_num] =\
                    cpu_num_core_data[index_value][cpu_num_index]
            return core_residency, cpu_num
        elif 5 == len(core_number):                                             # for individual one value reading #code for the specific [cpu_num][core_numbre] -- [row][column] is given
            core_residency = {}
            core_residency[cpu_num] = \
                cpu_num_core_data[int(core_number[4:])][cpu_num_index]
            return core_residency, cpu_num
        else:                                                                   #if input syntax is not correct
            library.write_log(lib_constants.LOG_INFO, "INFO: Input"
                " syntax is not correct", test_case_id, script_id,
                              "SocWatch_tool", "None",loglevel, tbd)
            return False,cpu_num
################################################################################
#  Function     : package_residency
#  Description  : parse the log file for package residency values
#  Param        : token, testcase id, scrip id, loglevel, tbd
#  Purpose      : package residency parsing for ALL and other cores
#  Return       : returns dictionary of available cpu's and cpu name
################################################################################


def package_residency(token, test_case_id, script_id, loglevel="ALL",
                      tbd="None"):
    cpu_num_c0=""

    log_file = []
    list_token = token.split()                                                  #convert to list
    script_dir = lib_constants.SCRIPTDIR                                        #store the Script dir location
    os.chdir(script_dir)                                                        #change directory

    log_file = glob.glob("*_SOC_LOG.csv")                                   #search for the file ending with _SOC_LOG.csv which will be the file to parse
                                                                #stores the file name

    log_file.sort(key=os.path.getmtime)

    if [] == log_file:                                                          #checks if file is present in the script directory
        library.write_log(lib_constants.LOG_WARNING, "Warning: File "
        "for C-State is not present or empty.", test_case_id, script_id,
                          "SocWatch_tool","None",loglevel, tbd)
        return False, ""
    else:
        log_file=log_file[-1]
    filein = open(log_file, "r")                                                #open file in read mode
    stream = filein.readlines()                                                 #store the contents in stream
    filein.close()                                                              #close the file

    req_token = list_token[3]                                                   #store the required token from the list

    if "ALL" in req_token.upper():                                              #if ALL in the token
        cpu_num = ""                                                            #put empty string as cpu_num
    else:
        cpu_num = req_token.split("_")[1].strip()                               #store cpunum after spliting the req_token
        if "C0" == cpu_num.upper() or "C1" == cpu_num.upper():
            cpu_num = "C0/C1"
            cpu_num_c0 = "C0"
        else:
            pass
        for n, ln in enumerate(stream):
             if ln.startswith("Package Residency"):                             #search for package residency string in file
                    break                                                       #break and store the line number
        n += 3
        c_state_value=[]                                                        #search for the cores present in the log file
        while -1 == stream[n].find("-"):
            c_state_array = stream[n].split(",")                                #store the key,values pair
            c_state_value.append(c_state_array[0].strip())                      #append the values in the lsit
            n+=1

            c_state_flag=0
            c_state_flag_c0 = 0
        for n, ln in enumerate(c_state_value):                                  #iterate through the cstate values
            if cpu_num == ln:                                                   #if requuired cpu name found in list
                c_state_flag=1                                                  #increment c_state_flag and break
                break
            elif cpu_num_c0 == ln:
                c_state_flag_c0 = 1
                break
            else:
                pass

        if c_state_flag_c0 == 1:
            cpu_num = cpu_num_c0

        if (0 == c_state_flag and 0 == c_state_flag_c0 ):
            return False, cpu_num
        else:
            pass

    for n, ln in enumerate(stream):                                             #iterate through the stream
        if ln.startswith("Package Residency"):                                  #search for Package residency and store the line number
            break
    n += 3
    package_residency = {}
    while -1 == stream[n].find("-"):                                            #when - is not found in line
        str_array = stream[n].split(",")                                        #split with comma
        package_residency[str_array[0].strip()] = str_array[1].strip()          #package residency is the 2nd part of string array
        n += 1
    return package_residency, cpu_num                                           #return the dictionary of values and the cpu name


################################################################################
#  Function     : compare_values
#  Description  : Comparing Two values
#  Param        : first value to compare, 2nd value to compare, operator,
#                   testcase id, script id, loglevel and tbd
#  Purpose      : Compares vales
#  Return       : Return PASS/FAIL as per comparison results
################################################################################


def compare_values(first_value, second_value, operation, test_case_id,script_id,
                                                loglevel="ALL", tbd="None"):
    value_stepm = first_value
    value_stepn = float(second_value)
    if '=' == operation:                                                        #Code to compare when first value and second values are equal
        if value_stepm == value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '>' == operation:                                                      #Code to compare when first value is greater than second value
        if value_stepm > value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '<' == operation:                                                      #Code to compare when first value is not greater than second value
        if value_stepm < value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '>=' == operation:                                                     #Code to compare when first value is greater than second value
        if value_stepm >= value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '<=' == operation:                                                     #Code to compare when first value is greater than second value
        if value_stepm <= value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '<>' == operation:                                                     #Code to compare when first value is greater than second value
        if value_stepm <> value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    elif '!=' == operation:                                                     #Code to compare when first value is greater than second value
        if value_stepm != value_stepn:
            return True                                                         #returns True when the condition matches
        else:
            return False
    else:
        return False

################################################################################

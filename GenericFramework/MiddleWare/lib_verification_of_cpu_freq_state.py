__author__ = "bchowdhx\kapilshx"

############################General library imports#############################
import os
import glob
import csv
import subprocess
import codecs
############################Local library imports###############################
import utils
import library
import lib_constants
import lib_set_bios
################################################################################
# Function Name : lib_verification_of_cpu_freq_state
# Parameters    : ostr, test_case_id, script_id,loglevel="ALL",
#                 tbd="None"
# Return Value  : True on success, False on failure
# Functionality : To verify the cpu frequency state from the TAT log file
################################################################################
def verification_of_cpu_freq_state(ostr, test_case_id, script_id,loglevel="ALL",
                       tbd="None"):                                             #parameter extraction
    try:                                                                        #get string from syntax
        tat_dir = utils.ReadConfig("TAT_TOOL","installedpath")                  #reads directory location of tat tool from config
        tat_exe = utils.ReadConfig("TAT_TOOL", "tat_cli")                       #reads tool name of tat from the config
        for items in [tat_dir, tat_exe]:                                        #checks if entry is there in config for tat_dir and tat_exe
            if "FAIL:" in items:
                library.write_log(lib_constants.LOG_WARNING, "Warning: Config "
                "entry missing for tat directory and exe name", test_case_id,
                               script_id, "None", "None", loglevel, tbd)
                return False
        if "STEP" in ostr.upper() and "LOG" in ostr.upper():
            ostr_list = ostr.upper().split()
            step, pos = utils.extract_parameter_from_token(ostr_list, "STEP",
                                                          "LOG", loglevel, tbd)
            file_path = utils.read_from_Resultfile(step)
        else:
            os.chdir(tat_dir)                                                   #change to tat directory
            cmd = tat_exe + " -p=" + str(lib_constants.THOUSAND) + " -t=" + \
                                 str(lib_constants.SIXTY_ONE)
            for file in glob.glob("TATMonitor*.csv"):                           #look for Tatmonitor named file
                os.remove(file)                                                 #remove the file if its present
            result = os.system(cmd)                                             #run the command and store the return value
            os.chdir(lib_constants.SCRIPTDIR)
            if 0 == result :                                                    #check for the return value if proper continue else return false
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfuly "
                     "generated log to check the frequency through TAT tool",
                        test_case_id, script_id, "None", "None", loglevel, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING,"WARNING:Failed to "
                     "generate log through TAT tool", test_case_id, script_id,
                                   "None", "None", loglevel, tbd)
                return False
            os.chdir(tat_dir)
            file = glob.glob("TATMonitor*.csv")                                 #look for Tatmonitor named file
            if file == []:                                                      #if file is not present in tat directory return false
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_WARNING, "WARNING: File not"
                    " available to parse in TAT folder", test_case_id, script_id,
                                  "None", "None", loglevel, tbd)
                return False
            else:
                file_name = file[0]                                             #store the filename
            file_path = os.path.join(tat_dir,file_name)
        if "ALL" in ostr.upper():                                               #if ALL p-state is mentioned in token
            result = get_column_number_p_state(ostr, file_path, test_case_id,
                                    script_id,loglevel, tbd)                    # function call to check the values with given condition
            if result:                                                          #return True if result is True
                return True
            else:
                return False
        else:
            result = get_column_number(ostr, file_path, test_case_id, script_id,
                                   loglevel, tbd)                               #function call to check the values with given condition
            if result:                                                          #return True if result is True
                return True
            else:
                return False                                                    #else return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due to %s"%e,
                        test_case_id, script_id, "None", "None", loglevel, tbd) #throw exception
################################################################################
# Function Name : get_lfm_hfm
# Parameters    : ostr, file_path to parse, test case id,
#                 script id
# Purpose       : Parsing csv to get LFM and HFM
# Return Value  : list of row nums
# Syntax        : verify parse log for <parameter>{ <delimiter>
#                   <expected_value>} from <source>
################################################################################
def get_lfm_hfm(ostr, file_path, test_case_id, script_id, loglevel="ALL",
                            tbd="None"):
    try:
        lfm, hfm = 0, 0
        col_num, col_num1, frequency_list = [], [], []
        tfile = open(file_path, "rb")                                           #read the csv file in binary read format
        reader = csv.reader(tfile)                                              #store the contents in a variable
        row_num, cnt = 0, 0
        for row in reader:                                                      #iterate through the header
            if 0 == row_num:
                header = row
                for i in header :
                    if "CPU" in i.upper() and "HFM(MHZ)" in i.upper():          #search the column for CPU and LFM to match CPUX-HFM(MHZ)
                        col_num.append(cnt)                                     #if found store in list
                    elif "CPU" in i.upper() and "LFM(MHZ)" in i.upper():        #search the column for CPU and LFM to match CPUX-LFM(MHZ)
                        col_num1.append(cnt)
                    cnt += 1
        value = get_values(file_path, col_num[0], test_case_id, script_id,
                                                    loglevel, tbd)             #call function to get the value from the particular row number
        value_lfm = get_values(file_path, col_num1[0], test_case_id, script_id,
                               loglevel, tbd)
        hfm = value[0]                                                          #extract hfm
        lfm = value_lfm[0]                                                      #extract lfm
        return lfm, hfm
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
################################################################################
# Function Name : get_column_number
# Parameters    : file_path to parse, test case id,
#                   script id
# Purpose       : Parsing csv to get the col no. which has CPUX-Frequency(MHz)
# Return Value  : list of row nums
# Syntax        : verify parse log for <parameter>{ <delimiter>
#                   <expected_value>} from <source>
################################################################################
def get_column_number(ostr, file_path, test_case_id, script_id,
                 loglevel="ALL", tbd="None"):                                   #pattern checking for parameters
    try:
        col_num, frequency_list = [], []
        tfile = open(file_path, "rb")                                           #read the csv file in binary read format
        reader = csv.reader(tfile)                                              #store the contents in a variable
        row_num, cnt = 0, 0
        for row in reader:                                                      #iterate through the header
            if 0 == row_num:
                header = row
                for i in header :
                    if "CPU" in i.upper() and "FREQUENCY(MHZ)" in i.upper():    #search the column for CPU and Frequency to match CPUX-Frequncy(MHZ)
                        col_num.append(cnt)                                     #if found store in list
                    cnt += 1
        for item in col_num:                                                    #iterate for number of entries got from the file
            value = get_values(file_path, item, test_case_id, script_id,
                                                    loglevel, tbd)              #call function to get the value from the particular row number
            frequency_list.extend(value)                                        #add the return values to a list

        result = calculate_frequency(ostr, file_path, frequency_list, test_case_id,
                                    script_id, loglevel, tbd)                   #function call to calculate the lfm/tfm/hfm logic
        if result:
            return True
        else:
            return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
################################################################################
# Function Name : get_values
# Parameters    : file_path , test case id,
#                   script id, loglevel and tbd
# Purpose       : Parsing csv to values in particular column according to rowno.
# Return Value  : list of values according to row num.
################################################################################
def get_values(file_path, item, test_case_id, script_id, loglevel="ALL",
               tbd="None"):
    try:
        col_num, result_list = [], []
        tfile = open(file_path, "rb")                                           #read the csv file in binary read format
        reader = csv.reader(tfile)                                              #store the contents in a variable
        row_num, cnt = 0, 0
        for row in reader:                                                      #iterate through the content
            if 0 == row_num:
                header = row
            else:
                colnum =0
                for col in row:
                    if colnum == item:
                        if col:
                            col = col.replace('"', "")                          #remove if quotes in entry
                            if col == 'Invalid' :                               #if invalid entry is there convert to 0 forcefully
                                col = 0
                            result_list.append((col))                           #append the value to the list
                    colnum += 1
            row_num += 1
        return result_list
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
################################################################################
# Function Name : calculate_frequency
# Parameters    : ostr, values, path , test case id,
#                   script id, loglevel and tbd
# Purpose       : Checking lfm tfm hfm logic on the returned list
# Return Value  : list of values according to row num.
# Syntax        : verify parse log for <parameter>{ <delimiter>
#                   <expected_value>} from <source>
################################################################################
def calculate_frequency(ostr, filepath, values, test_case_id, script_id,
                        loglevel="ALL", tbd="None"):
    try:
        truth_table =[]
        LFM, HFM = get_lfm_hfm(ostr, filepath, test_case_id, script_id,
                               loglevel, tbd)

        if "LFM" in ostr.upper():                                               #if LFM in input token
            lfm_count = 0
            for item in values:                                                 #iterate through the values list
                if int(item) < int(LFM)+50 and int(item) > int(LFM)-50:         #check for item within range of LFM+50 and LFM-50
                    lfm_count += 1
                else:
                    pass
            print("lfm_count",lfm_count)
            if lfm_count >= ((len(values))/5):
                library.write_log(lib_constants.LOG_INFO, "Info: Values "
                "are meeting LFM condition", "None", "None", loglevel, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "Warning: Values "
                "are not meeting LFM condition", "None", "None", loglevel, tbd)
                return False

        elif "HFM" in ostr.upper():                                             #if HFM in input token
            hfm_count = 0
            for item in values:                                                 #iterate through the values list
                if int(item) < int(HFM)+50 and int(item) > int(HFM)-50:         #check for item within range of HFM+50 and HFM-50
                    hfm_count += 1
                else:
                    pass
            print("hfm_count",hfm_count)
            if hfm_count >= ((len(values))/5):
                library.write_log(lib_constants.LOG_INFO, "Info: Values "
                "are meeting HFM condition", "None", "None", loglevel, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "Warning: Values "
                "are not meeting HFM condition", "None", "None", loglevel, tbd)
                return False
        elif "TFM" in ostr.upper():                                             #if TFM in input token
            tfm_count = 0
            for item in values:                                                 #iterate through the values list
                if int(item) > int(HFM):                                        #check if item value is more than HFM
                    tfm_count += 1
                else:
                    pass
            if tfm_count >= ((len(values))/5):
                library.write_log(lib_constants.LOG_INFO, "Info: Values "
                "are meeting TFM condition", "None", "None", loglevel, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "Warning: Values "
                "are not meeting TFM condition", "None", "None", loglevel, tbd)
                return False
        elif "ALL" in ostr.upper():                                             #Not implemented- Logic needs discussion
            pass
            if 0 in truth_table:
                library.write_log(lib_constants.LOG_WARNING, "Warning: Values "
        "are not meeting All P-States condition", "None", "None", loglevel, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "Info: Values "
        "are meeting All P-States condition", "None", "None", loglevel, tbd)
                return True
        else:
            library.write_log(lib_constants.LOG_INFO, "Info: Input syntax is "
                "correct", "None", "None", loglevel, tbd)
            return True
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
################################################################################
# Function Name : get_column_number_for_all_p_states
# Parameters    : ostr, file_path to parse, test case id,
#                   script id
# Purpose       : Parsing csv to get the CPU frequencies for first two
#                 consecutive cycles
# Return Value  : Return true if
################################################################################
def get_column_number_p_state(ostr, file_path, test_case_id, script_id,
                 loglevel="ALL", tbd="None"):                                   #pattern checking for parameters
    try:
        col_num, frequency_list,frequency_list_p_state,value = [], [], [], []
        tfile = open(file_path, "rb")                                           #read the csv file in binary read format
        reader = csv.reader(tfile)                                              #store the contents in a variable
        row_num, cnt, cnt_p_state,col_num_p_state, = 0, 0, 0, 0
        for row in reader:                                                      #iterate through the header
            if 0 == row_num:
                header = row
                for i in header :
                    if "CPU" in i.upper() and "-FREQUENCY(MHZ)" in i.upper():   #search the column for CPU and Frequency to match CPUX-Frequncy(MHZ)
                        col_num.append(cnt)                                     #if found store in list
                    if "CPU-INFO-CURRENT P STATE" in i.upper():                 #search the column for CPU-Info-Current P State to match cpu for all p-state
                        col_num_p_state = cnt                                   #if found store in list
                    cnt += 1
        frequency_list_p_state = get_values(file_path, col_num_p_state,
                                    test_case_id, script_id,loglevel, tbd)      #call function to get the value from the particular row number
        for item_new in frequency_list_p_state:
            if 'Not Supported' in frequency_list_p_state:
                library.write_log(lib_constants.LOG_INFO, "INFO: Under "
                "the P-state cycle column value is showing 'not supported' "
                    "in csv file", test_case_id, script_id,
                              "None", "None",loglevel, tbd)
                return False
            else:
                pass
        index_start_p_state = index_end_p_state = index_start_p_state_value \
        = index_end_second_p_state = index_start_second_p_state =\
            index_start_second_p_state_value = 0
        p_state_start_flag = False
        p_state_end_flag = False
        p_state_exceed_range_flag = False
        p_state_second_end_flag = False
        p_state_second_exceed_range_flag = False
        for index,item in enumerate(frequency_list_p_state):                    #loop to get the p-state cycle from the log file
            if len(frequency_list_p_state) != (index+1):                        #condition to check the list index out of range
                if int(frequency_list_p_state[index+1]) < \
                        int(frequency_list_p_state[index]):                     #if next p-state cycle is less then previos cone then true
                    p_state_start_flag = True
                    index_start_p_state = index + 1
                    index_start_p_state_value = index_start_p_state
                    for index_end,item_end in enumerate(frequency_list_p_state):#loop to iterate the first P-state cycle
                        if len(frequency_list_p_state) != \
                                                index_end+index_start_p_state+1:#condition to check the list index out of range
                            if int(frequency_list_p_state
                            [index_start_p_state_value+1]) < \
                        int(frequency_list_p_state[index_start_p_state_value]): #if next p-state cycle is less then previos cone then true
                                p_state_end_flag = True                         #if first P-state cycle is found in log file
                                index_end_p_state = index_start_p_state_value
                                index_start_second_p_state_value = \
                                    index_start_p_state_value+1
                                index_start_second_p_state = \
                                    index_start_second_p_state_value
                                for index_second_end,item_second_end in \
                                        enumerate(frequency_list_p_state):      #loop to iterate the second P-state cycle
                                    if len(frequency_list_p_state) != \
                                index_second_end+index_start_second_p_state+1:  #condition to check the list index out of range
                                        if int\
                (frequency_list_p_state[index_start_second_p_state_value+1]) < \
                int(frequency_list_p_state[index_start_second_p_state_value]):
                                            p_state_second_end_flag = True      #if second P-state cycle is found in log file
                                            index_end_second_p_state = \
                                                index_start_second_p_state_value
                                            break
                                        else:
                                            index_start_second_p_state_value +=1
                                    else:
                                        p_state_second_exceed_range_flag = True #if second P-state cycle is not found in log file
                                        break
                                if True == p_state_second_end_flag or True == \
                                        p_state_second_exceed_range_flag:
                                    break
                            else:
                                index_start_p_state_value+=1
                        else:
                            p_state_exceed_range_flag = True                    #if the p-state frequency list index is out of range
                            break
                    if True == p_state_end_flag  or\
            True == p_state_exceed_range_flag or True ==\
            p_state_second_end_flag or True == p_state_second_exceed_range_flag:#if Either the p-state frequency list index is out of range or first and second P-state cycle is found in log file
                        break
                else:
                    pass
            else:
                break
        if True == p_state_start_flag and True == p_state_end_flag and \
                        True == p_state_second_end_flag:                        #if first and second P-state cycle is found in log file
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "P-State cycle is found in the log file ", test_case_id, script_id,
                              "None", "None",loglevel, tbd)
            pass
        else:                                                                   #if first and second P-state cycle is not found in log file
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "P-State cycle is not found in the log file ", test_case_id,
                              script_id, "None", "None",loglevel, tbd)
            return False

        LFM, HFM = get_lfm_hfm(ostr, file_path, test_case_id, script_id,
                               loglevel, tbd)                                   #To get the LFM and HFM value from the log file
        LFM_upper_range = int(LFM)+lib_constants.CPU_FREQ_DIFFERENCE            #To convert upper range  add 100 and for lower range subtract 100 from actual LFM & HFM value
        LFM_lower_range = int(LFM)-lib_constants.CPU_FREQ_DIFFERENCE
        HFM_upper_range = int(HFM)+lib_constants.CPU_FREQ_DIFFERENCE
        HFM_lower_range = int(HFM)-lib_constants.CPU_FREQ_DIFFERENCE
        cpu_frequency_flag = []
        for item in col_num:                                                    #iterate for number of entries got from the file
            value = get_values(file_path, item, test_case_id, script_id,
                                                    loglevel, tbd)              #call function to get the value from the particular row number
            list = []
            list = [int(value[index_start_p_state]),
        int(value[index_end_p_state]),int(value[index_start_second_p_state]),
                    int(value[index_end_second_p_state])]
            if ((list[0] <= HFM_upper_range and list[0] >= HFM_lower_range)) \
        and ((list[1] <= LFM_upper_range) and (list[1] >= LFM_lower_range)) \
        and ((list[2] <= HFM_upper_range) and (list[2] >= HFM_lower_range)) \
            and ((list[3] <= LFM_upper_range) and (list[3] >= LFM_lower_range)):#check if for both the P-state cycle ,CPU frequencies are found under LFM+-100 or HFM +-100
                cpu_frequency_flag.append(1)                                    #store 1 into the list if above condition true else stroe 0
            else:
                cpu_frequency_flag.append(0)
        if 0 in cpu_frequency_flag:                                             #if CPU frequencies are not matching the criteria for respective P- state
            library.write_log(lib_constants.LOG_WARNING, "Warning: Values "
    "are not meeting the difference criteria of CPU frequencies"
                " for all P-state condition", test_case_id, script_id,
                              "None", "None", loglevel, tbd)
            return False
        else:                                                                   # now check for all 1 in the appended list, if 1 is present return True means frequencies are proper
            library.write_log(lib_constants.LOG_INFO, "Info: Values "
        "are meeting the difference criteria of CPU frequencies "
                    "for all P-state condition", test_case_id, script_id,
                              "None", "None", loglevel, tbd)
            return True
    except Exception as e:                                                      # Exception occurs in get_column_number_p_state() library function
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception occurs in "
            "get_column_number_p_state() library function due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
        return False
################################################################################
# Function Name : bios_settings_for_cpu_freq_state
# Parameters    : test case id, script id, loglevel, tbd
# Purpose       : To do bios setting for CPU frequency state
# Return Value  : True on success ,false otherwise
################################################################################
def bios_settings_for_cpu_freq_state(test_case_id, script_id,
                 loglevel="ALL", tbd="None"):
    try:
        bios_conf_cmd = "BIOSConf.exe updateq "
        bios_option_flag = True
        os.chdir(lib_constants.EPCSTOOLPATH)
        for option in lib_constants.TURBOMODE_INTELSPEEDSHIFT:
            command = bios_conf_cmd + option +"> log.txt"
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,   #run command in subprocess
                                     stderr=subprocess.STDOUT,
                                 stdin=subprocess.PIPE)
            exec_out = p.communicate()[0]
            with codecs.open('log.txt','r',encoding='utf8') as reader:
                for line in reader:
                    if 'Requested operations completed successfully' in line:
                        library.write_log(lib_constants.LOG_INFO,"INFO: Bios "
                    "Updated for quid%s"%option,test_case_id,script_id,"None",
                                          "None",loglevel, tbd)
                    elif 'Updating given UQI from commandline incomplete' in line:#if option is not updated in bios
                        library.write_log(lib_constants.LOG_INFO,"INFO: Bios "
                    "Updated failed for quid%s"%option,test_case_id,script_id,
                                          "None","None",loglevel, tbd)
                        bios_option_flag = False
        if False == bios_option_flag:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Failed "
            "to update the bios settings",
             test_case_id, script_id, "None", "None", loglevel, tbd)
            return False
        else:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_INFO,": INFO Bios "
            "option updated successfully",
             test_case_id, script_id, "None", "None", loglevel, tbd)
            return True
    except Exception as e:                                                      # Exception occurs in bios_settings_for_cpu_freq_state() library function
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception occurs in "
            "bios_settings_for_cpu_freq_state() library function due to %s"%e,
             test_case_id, script_id, "None", "None", loglevel, tbd)
        return False
################################################################################
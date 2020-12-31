__author__ = 'jkmody'

# Global Python Imports
import configparser
import csv
import glob
import math
import os
import re
import shutil
import sys
import time
import zipfile
import subprocess
from datetime import datetime as dt
from collections import namedtuple

# Local Python Imports
import library
import lib_constants

# Global Variables
script_id = ''
TC_id = ''
TC_id_info = []
dest_path = ''
platform_data = []
platform_dir_path = ""
dir_path_platform = ""
step_info = []
global ostr
ostr = ""

################################################################################
# Function Name : create_res_file
# Parameters    : dir_path
# Functionality : Creates res.ini for entering every step result
# Return Value  : None
################################################################################


def create_res_file(dir_path):
    f = open(dir_path + "\Results.ini", "w")                                    # Creating the Result.ini file in write mode
    f.close()                                                                   # Closing the Result.ini file

################################################################################
# Function Name : set_step_no
# Parameters    : step = Step no, dir = Directory
# Functionality : sets step number in step.txt
# Return Value  : None
################################################################################


def set_step_no(step, dir):
    f = open(dir + "\step.txt", "w")                                            # Opening the Step.txt file in write mode
    f.writelines(str(step))                                                     # Writing Step No in Step.txt file
    f.close()                                                                   # Closing the Step.txt file

################################################################################
# Function Name : ProcessLine
# Parameters    : test step
# Functionality : Splits the test step on spaces and converts them to upper case
# Return Value  : None
################################################################################


def ProcessLine(line):
    global ostr
    ostr = line
    s = line.upper()                                                            # Converting the String(Token) to Upper Case
    new_str = re.split('\s+', s)                                                # Splitting the String(Token) based on the space("\s")
    return new_str

################################################################################
# Function Name : get_original_str
# Parameters    : none
# Functionality : gives the entire test step
# Return Value  : Returns the entire string in tact
################################################################################


def get_original_str():
    return ostr                                                                 # returns the test step

################################################################################
# Function Name : remove_negative
# Parameters    : script_id = script id
# Functionality : Extracts the negative tag from the test step and
#                 interchanges exit(0) with exit(1)
# Return Value  : None
################################################################################


def remove_negative(script_id):

    file = glob.glob("*.py")
    file_check = []

    script_id = script_id.split("\\")[-1].split(".py")[0]
    check_file = []
    for item in file:
        if script_id in item:
            check_file.append(item)

    for item in check_file:
        if "Reboot" in item:
            pass
        else:
            with open(item, "r") as fin:
                with open("out.txt", "w") as fout:                              # Creating out.txt in write mode
                    for line in fin:
                        if "sys.exit(lib_constants.EXIT_SUCCESS)" in line:
                            fout.write(line.replace("sys.exit(lib_constants.EXIT_"
                                                    "SUCCESS)",
                                                    "sys.exit(lib_constants.EXIT_"
                                                    "FAILURE)"))                # Replacing the sys.exit(0) with sys.exit(1) and writing it to out file
                        elif "sys.exit(lib_constants.EXIT_FAILURE)" in line:
                            fout.write(line.replace("sys.exit(lib_constants.EXIT_"
                                                    "FAILURE)",
                                                    "sys.exit(lib_constants.EXIT_"
                                                    "SUCCESS)"))                # Replacing the sys.exit(0) with sys.exit(1) and writing it to out file
                        elif "lib_constants.LOG_PASS" in line and "PASS:" in line:
                            fout.write(line.replace("PASS", "FAIL"))
                        elif "lib_constants.LOG_FAIL" in line and "FAIL:" in line:
                            fout.write(line.replace("FAIL", "PASS"))
                        else:
                            fout.write(line)

            with open("out.txt", "r") as fin:                                   # open out file in read mode
                with open(item, "w") as fout:
                        for line in fin:
                            fout.write(line)
    os.remove("out.txt")                                                        # remove the out file if already exists

################################################################################
# Function Name     : write_to_file
# Parameters        : code to be written to script file
# Functionality     : Writes the given string to a file "filename"
# Return Value      : None
################################################################################


def write_to_file(str, filename, timeout='600'):

    ts = time.strftime("%d/%m/%Y %H:%M:%S\n")
    f = open(filename, "w")

    try:
        param_list = "#timeout=" + timeout + ","
        f.writelines(param_list + "\n")                                         #code for adding attributes for JSON toolcase
    except Exception as e:
        with open(lib_constants.PARSERLOG, "a") as file_append:
            file_append.write("%s" % str(e))                                    #code for adding future variable to all generated script files

    f.writelines("#This is automatically generated. Timestamp: " + ts)

    extra_parameters = '''
import sys

try:
    log_level = sys.argv[1]
except:
    log_level = "ALL"

try:
    tbd = sys.argv[2]
except:
    tbd = "None"
'''

    f.writelines(extra_parameters)
    f.writelines(str)
    f.close()

################################################################################
# Function Name : write_to_Resultfile
# Parameters    : result
# Functionality : every test step result is written to this file
# Return Value  : None
################################################################################


def write_to_Resultfile(result, script_id):

    if "\\" in script_id:                                                       # Check if script id is separated by ' \\ '
        script_id_info = script_id.split("\\")[1].strip()
    else:
        script_id_info = script_id

    step_id_info = script_id_info.split("-")

    if ".py".lower() in step_id_info[3].lower():
        step_id = step_id_info[3].split(".py")[0].strip()                       # Splitting the test
    else:
        step_id = step_id_info[3].strip()

    f = open(lib_constants.SCRIPTDIR + "\\Results.ini", "a")
    str_ = "[Step-" + str(step_id).strip() + "]"
    f.writelines("\n" + str_.strip() + "\n")                                    # Writing the Step Number in Result.ini file
    str_ = "Result=" + str(result).strip()
    f.writelines(str_.strip()+"\n")                                             # Writing the Result in the Result.ini file
    f.close()

################################################################################
# Function Name : ReadConfig
# Parameters    : tag, value
# Functionality : Reads config variables
# Return Value  : None
################################################################################


def ReadConfig(tag, value):
    def ConfigFinder(config_path, tag, value):
        # if os.path.exists(lib_constants.SCRIPTDIR + "\\Config.ini"):
        #     config_path = lib_constants.SCRIPTDIR + "\\Config.ini"
        # else:
        #     config_path = lib_constants.MIDDLEWARE_PATH + "\\Config.ini"

        # if "source" in config_path.lower():
        #     config_path = lib_constants.CONFIGPATH + "\\Config" + \
        #         dest_path + ".ini"

        if os.path.exists(config_path):
            with open(config_path, 'r') as file_:
                data = file_.readlines()
            flag = 0
            for i in range(len(data)):
                if ("[" + tag.lower() + "]") in data[i].lower():                # Comparing the Tag Name
                    flag = 1
                    j = i + 1
                    while True:
                        if value.lower() in data[j].lower():                    # Comparing whether the Variable is present in the above selected tag or not
                            tag_value = data[j].split("=")[1].strip()
                            if (data[j].split("=")[0].strip().lower() ==
                                    value.lower()):
                                if len(tag_value) == 0:
                                    str = "INFO: Value given is Blank"
                                    print(str)
                                    return False
                                else:
                                    return tag_value
                        j = j + 1
                        if j == len(data) or "[" in data[j]:
                            str = "INFO: Value incorrect or %s not "\
                                "contained the variable" % (config_path)
                            print(str)
                            return False
            if flag == 0:
                str = "INFO: Values are incorrect or %s does not " \
                    "contain the TAG" % (config_path)
                print(str)
                return False
        else:
            str = "INFO: %s is not present" % (config_path)
            print(str)
            return False
    matched_value = ""
    config_list = []
    middleware_config = lib_constants.MIDDLEWARE_PATH + "\\Config.ini"
    config_list.append(middleware_config)
    script_config = lib_constants.SCRIPTDIR + "\\Config.ini"
    config_list.append(script_config)
    for config_ele in config_list:
        try:
            if "source" in config_ele.lower():
                source_path = lib_constants.CONFIGPATH + "\\Config"
                + dest_path + ".ini"
                config_ele = source_path
            matched_value = ConfigFinder(config_ele, tag, value)
            if not matched_value:
                matched_value = ""
                print("INFO: Check next available config file")
                continue
            else:
                print("INFO: Matched in %s" % (config_ele))
                return matched_value
        except Exception:
            print("WARNING: Exception occurred during %s parsing" % (config_ele))
    if not matched_value:
        warn_str = "Value is not matched in all config files"
        print("WARNING: " + warn_str)
        ret_str = "FAIL: " + warn_str
        return ret_str


################################################################################
# Function Name : generate_syntaxHandlerError
# Parameters    : none
# Functionality : Generates the failures if any in syntax handler
# Return Value  : None
################################################################################


def generate_syntaxHandlerError(TC_id, Script_ID, token):

    """
    Function name   : generate_syntaxHandlerError
    Description     : Generate CSV file with Syntax Handler Failure report
    Parameters      : Script_ID,token,cur_dir
    Returns         : 1 for fail 0 for pass
    Script by       : jbishtx
    Dependent func  : functons availble in Syntax_Handler.py
    """

    Syntax = ' '.join(token)
    mylist1 = "Test Case ID, Script ID, Grammar Syntax, Module, Remarks"
    mylist = TC_id + "," + Script_ID + "," + Syntax + "," + \
        "Syntax-Handler,FAIL"

    if not os.path.exists(lib_constants.SYNTAXLOG):
        fd = open(lib_constants.SYNTAXLOG, 'wb')
        fd.write(mylist1)
        fd.write('\n')
        fd.close()
    else:
        pass

    fd = open(lib_constants.SYNTAXLOG, 'ab')
    fd.write(mylist)
    fd.write('\n')
    fd.close()

    inputCSV = open(lib_constants.SYNTAXLOG, 'rb')
    outputCSV = open(lib_constants.SOURCEPATH + "\\OUTPUT.csv", 'wb')

    appendCSV = open(lib_constants.SOURCEPATH + "\\OUTPUT.csv", 'ab')           # Prepare output csv for appending

    cr = csv.reader(inputCSV)                                                   # Create reader object

    cw = csv.writer(outputCSV)                                                  # Create writer object

    ca = csv.writer(appendCSV)                                                  # Create writer object for append

    for row in cr:
        if row or any(row) or any(field.strip() for field in row):
            ca.writerow(row)                                                    # Writing the Failure in Syntax-handler.csv file

    inputCSV.close()
    outputCSV.close()
    appendCSV.close()
    time.sleep(5)

    os.remove(lib_constants.SYNTAXLOG)
    os.rename(lib_constants.SOURCEPATH + "\\OUTPUT.csv",
              lib_constants.SYNTAXLOG)

################################################################################
# Function Name : package_verification
# Parameters    : dest_path = destination path; platform_data = platform,
#                 TC_id_info = Testcase id
# Functionality : Verifies if the package generated is correct or not
# Return Value  : None
################################################################################


def package_verification(dest_path, platform_data, TC_id_info):

    if os.path.exists(lib_constants.SYNTAXLOG):
        with open(lib_constants.SYNTAXLOG, "rb") as file_:
            data = file_.readlines()                                            # Reading the Syntax Mismatch failure

        error_TC_id = []                                                        # declaring empty list to variable

        for i in range(len(data)):
            if "Test Case ID" in data[i]:                                       # checking if test case id exist in
                pass
            else:
                error_TC_id.append(data[i].split(",")[0].strip())               # appends the testcase id into the empty list created before

        error_TC_id = list(set(error_TC_id))
        files = glob.glob(lib_constants.OUTPUTPATH + "\\" + dest_path +
                          "\\" + platform_data[0] + "\\*")

        for i in range(len(files)):
            if os.path.isdir(files[i]):
                if files[i].split("\\")[-1].strip() in error_TC_id:
                    f = lib_constants.OUTPUTPATH + "\\" + dest_path + "\\" + \
                        platform_data[0] + "\\" + \
                        files[i].split("\\")[-1].strip()
                    command = '''rmdir /S /Q "''' + f + '''"'''
                    os.system(command)                                          # Deleting the Test Case Folder Which Contains the Syntax Mismatch Error

        check = len(TC_id_info)
        i = 0

        while i != check:
            flag = False
            for j in range(len(error_TC_id)):
                if str(TC_id_info[i]) == str(error_TC_id[j]):
                    step_info[i] = 0
                    check = check-1
                    flag = True
                    break
            if flag == False:
                i = i+1
    else:
        with open(lib_constants.OUTPUTPATH + "\\" + dest_path + "\\" +
                  platform_data[0] + "\\Package_log.csv", "w") as f_:
            f_.write("Test Case ID, Script ID, Grammar Syntax, Module, "
                     "Remarks\n")

    files = []

    for i in range(len(TC_id_info)):
        files.append(lib_constants.OUTPUTPATH + "\\" + dest_path + "\\" +
                     platform_data[0] + "\\" + TC_id_info[i])

    for i in range(len(files)):
        if step_info[i] == 0:
            continue

        if os.path.isdir(files[i]):
            config_path = lib_constants.CONFIGPATH + "\\Config_" + \
                          dest_path + ".ini"
            shutil.copy(config_path, files[i] + "\\Config.ini")                 # Copying Config.ini file to individual TC folder
            script_no = []
            file = glob.glob(files[i] + "\\CSS-IVE-*")
            for j in range(len(file)):
                step_no = file[j].split("\\")[-1].split("-")[3].strip()

                if ".py" in step_no:
                    step_no = step_no.split(".py")[0].strip()

                script_no.append(int(step_no))

            script_no = list(set(script_no))
            script_no = sorted(script_no)
            check = 0

            while check != int(step_info[i]):
                check = check+1

                if check in script_no:
                    pass
                else:
                    try:
                        f = lib_constants.OUTPUTPATH + "\\" + dest_path + \
                            "\\" + platform_data[0] + "\\" + \
                            files[i].split("\\")[-1].strip()
                        command = '''rmdir /S /Q "''' + f + '''"'''
                        os.system(command)                                      # Deleting the Test Case Folder Which Contains the Code Generation Error
                    except:
                        pass

                    TC = files[i].split("\\")[-1].strip()
                    script = TC + "-" + str(check) + ".py"

                    if os.path.exists(lib_constants.SYNTAXLOG):
                        with open(lib_constants.SYNTAXLOG, "a") as f_:
                            f_.write(TC + "," + script +
                                     ",,Code-Generator,FAIL\n")
                    else:
                        with open(lib_constants.OUTPUTPATH + "\\" +
                                  dest_path + "\\" + platform_data[0] +
                                  "\\Package_log.csv", "a") as f_:
                            f_.write(TC + "," + script +
                                     ",,Code-Generator,FAIL\n")
    if os.path.exists(lib_constants.SYNTAXLOG):
        shutil.move(lib_constants.SYNTAXLOG, lib_constants.OUTPUTPATH + "\\" +
                    dest_path + "\\" + platform_data[0] + "\\Package_log.csv")  # Renaming the file to Package_log.csv


################################################################################
# Function Name : Parse_xml
# Parameters : XML file
# Functionality: Parses XML file for test steps
# Return Value : steps,Platform Information ,Test Case Id
################################################################################


def Parse_xml(filename, dest_path):

    global TC_id
    global script_id
    parser_path = lib_constants.SOURCEPATH
    curr_path = parser_path
    path = parser_path

    os.chdir(lib_constants.OUTPUTPATH + "\\" + dest_path)
    file_name = filename.split("\\")[-1].strip()
    TC_id = file_name.split(".")[0].strip()
    TC_id_info.append(TC_id)
    dir_path = os.path.join(lib_constants.OUTPUTPATH + "\\" + dest_path, TC_id)

    if os.path.exists(dir_path) == True:
        command = '''rmdir /S /Q "''' + dir_path + '''"'''
        os.system(command)                                                      # Deleting the Existing Test Case Folder

    os.mkdir(TC_id)                                                             # Creating the Test Case Folder
    create_res_file(dir_path)

    with open(lib_constants.INPUTPATH + "\\" + filename.split("\\")[-2].strip()
              + "\\" + file_name, 'r') as file_:
        data = file_.read().decode('utf-8', 'ignore').replace('\n', '')         # Reading The Xml file
    platform = ""

    try:
        first = "<Applicable_platforms>"
        last = "</Applicable_platforms>"
        start = data.index(first) + len(first)
        end = data.index(last, start)
        platform = data[start:end]                                              # Extracting the Platform Information
    except ValueError:
        with open(lib_constants.PARSERLOG, "a") as file_append:
            file_append.write("ERROR: due to ValueError")

    platform_dir_path = lib_constants.OUTPUTPATH + "\\" + dest_path + "\\" + \
        platform

    dir_path_platform = os.path.join(lib_constants.OUTPUTPATH + "\\" +
                                     dest_path, TC_id + "-" + platform)

    if os.path.exists(dir_path_platform) == True:
        command = '''rmdir /S /Q "''' + dir_path_platform + '''"'''
        os.system(command)

    platform_info = []
    platform_info = platform.split(",")

    for i in range(len(platform_info)):
        platform_info[i] = platform_info[i].strip()
        platform_data.append(platform_info[i].strip())

    if os.path.exists(platform_dir_path) == True:
        pass
    else:
        os.mkdir(platform_dir_path)                                             # Creating the Folder for Specific Platform(i.e. KBL)

    os.mkdir(TC_id + "-" + platform)
    create_res_file(dir_path_platform)                                          # Creating The Result.ini file
    os.chdir(dir_path)
    word = "ID="
    count = int(math.ceil(float(data.count(word))))                             # Getting the Step Count
    steps = []

    for i in range(int(count)-1):
            try:
                first = "<Step" + str(i+1)
                last = "</Step" + str(i+1)
                start = data.index(first) + len(first)
                end = data.index(last, start)
                steps.append(data[start:end])                                   # Extracting The Steps from Xml File
            except ValueError:
                with open(lib_constants.PARSERLOG, "a") as file_append:
                    file_append.write("ERROR: due to ValueError")
    return steps, platform_info, TC_id

################################################################################
# Function Name : Parse_txt
# Parameters    : txt file
# Functionality : Parses txt file for test steps
# Return Value  : steps,"NONE",Test Case Id
################################################################################


def Parse_txt(file_name):
    global TC_id
    steps = []
    files = [file_name]

    for i in range(len(files)):
        line_no = 0
        file = files[i].split("\\")[-1].strip()
        TC_id = file.split(".")[0].strip()
        file = lib_constants.INPUTPATH + "\\" + file
        dir_path = os.path.join(lib_constants.OUTPUTPATH, TC_id)

        if os.path.exists(dir_path) == True:
             command = '''rmdir /S /Q "''' + dir_path + '''"'''
             os.system(command)                                                 # Deleting the Existing Test Case Folder

        os.mkdir(lib_constants.OUTPUTPATH + "\\" + TC_id)                       # Creating the Test Case Folder
        create_res_file(dir_path)                                               # Creating Result.ini file in Test Case Folder
        f = open(file, "r")

        for line in f:
            line = line.strip()
            line_no = line_no + 1
            set_step_no(line_no, dir_path)
            original_str = line
            steps.append(original_str)                                          # Extracting Steps from text file
        f.close()
    return steps, "NONE", TC_id

################################################################################
# Function Name : code_generator_call()
# Parameters    : Code Generator Function Call,
#                 Parameters to pass(token,Tc id,Script id)
# Functionality : Call back function definition
# Return Value  : None
################################################################################


def code_generator_call(function, params):

    try:
        function(*params)                                                       # Calling the Code Generator Function
    except Exception as e:
        with open(lib_constants.PARSERLOG, "a") as file_append:
            file_append.write("ERROR: due to %s" % e)

################################################################################
# Function Name : extract_grammar()
# Parameters    : tag = tag name; str_ = String name
# Functionality : It will extract step between the
#                 platform tag(i.e. <APL>step</APL>)
# Return Value  : Step
################################################################################


def extract_grammar(str_, tag):

    try:
        first = "<" + tag + ">"
        last = "</"

        if last in str_:
            start = str_.index(first) + len(first)
            end = str_.index(last, start)
            return str_[start:end].strip()                                      # Returning the extracted step between the platform tag
        else:
            start = str_.index(first) + len(first)
            return str_[start:].strip()
    except ValueError:
        return ""

################################################################################
# Function Name : check()
# Parameters    : step = testcase step; platform= Platform; flag= out flag;
#                 RE_dict= regular expression dictionary; script_id=script id;
#                 TC_id = testcase id
# Functionality : Check platform info and will generate the scripts based on it
# Return Value  : None
################################################################################


def check(step, platform, flag, RE_dict, script_id, TC_id, package_type):

    plt_open = ["< " + platform + ">", "<" + platform + " >",
                "< " + platform + " >"]
    plt_close = ["</ " + platform + ">", "</" + platform + " >",
                 "</ " + platform + " >"]

    if platform.upper()+" Negative=\"True\"" in step:                           #Checking for Platform Specific Negative Tag for True Value
        flag = "True"
        step = step.replace(platform.upper()+" Negative=\"True\"", platform)

    if platform.upper()+" Negative=\"False\"" in step:                          #Checking for Platform Specific Negative Tag for False Value
        flag = "False"
        step = step.replace(platform.upper()+" Negative=\"False\"", platform)
    for j in range(len(plt_open)):
        if plt_open[j] in step:
            step = step.replace(plt_open[j], "<" + platform + ">")              #Removing the platform information(i.e. <KBL:>) from the test steps

    for l in range(len(plt_close)):
        if plt_close[l] in step:
            step = step.replace(plt_close[l], "</" + platform + ">")            #Removing the platform information(i.e. </KBL:>) from the test steps

    final_grammar = extract_grammar(step, platform)                             #Extracting the Grammar From The Test Step
    token = ProcessLine(final_grammar)

    os.chdir(dir_path_platform)
    try:
        if "negative" in token[0].lower():
            token[0] = token[0].split("NEGATIVE:")[1]                           # Removing the Negative Keyword from the test step
            if token[0] == '':
                del token[0]
        ostr = get_original_str()
        keys = list(RE_dict.keys())
        key_match = False

        for k in range(len(keys)):
            if re.match(keys[k], ostr, re.I):                                   # Comparing the RE with Test Step
                try:
                    code_generator_call(RE_dict[keys[k]], [token, TC_id,
                                                           script_id,
                                                           package_type, flag,
                                                           platform])           # Passing the function pointer to code generator function for Platform Specific Test Step
                except Exception as e:
                    with open(lib_constants.PARSERLOG, "a") as file_append:
                        file_append.write("ERROR: due to %s" % e)
                key_match = True
                break

        if key_match == False:
            generate_syntaxHandlerError(TC_id, script_id, token)                # writing Syntax Mismatch error
    except Exception as e:
        with open(lib_constants.PARSERLOG, "a") as file_append:
            file_append.write("ERROR: due to %s" % e)

    if flag == "True":
        try:
            remove_negative(script_id)                                          # Calling Function to remove negative Tag
        except Exception as e:
            with open(lib_constants.PARSERLOG, "a") as file_append:
                file_append.write("ERROR: due to %s" % e)

###############################################################################
# Function Name : folder_creation()
# Parameters    : platform_info: Platform information
# Functionality : Folders for each platform get created for holding test scripts
# Return Value  : None
###############################################################################


def folder_creation(platform_info):

    os.chdir(lib_constants.OUTPUTPATH + "\\" + dest_path)
    files = glob.glob(lib_constants.OUTPUTPATH + "\\" + dest_path + "\\*")

    for f in files:
        if platform_info not in f:
            command = '''rmdir /S /Q "''' + f + '''"'''
            os.system(command)                                              #Removing The Folders which are not platform specific

    files = glob.glob(lib_constants.OUTPUTPATH + "\\" + dest_path + "\\*")

    for f in files:
        if "-" + platform_info in f:
            if (os.path.exists(platform_dir_path + "\\" + f.split("\\")[-1].
               split("-" + platform_info)[0].strip()) == True):
                dir_platform = platform_dir_path + "\\" + \
                    f.split("\\")[-1].split("-"+platform_info)[0].strip()
                command = '''rmdir /S /Q "''' + dir_platform + '''"'''
                os.system(command)
            shutil.move(f, platform_dir_path + "\\" + f.split("\\")[-1].
                        split("-" + platform_info)[0].strip())                  #Moving the files into the TC-ID specific Folder(i.e (KBL/BXT/CNL/APL/GLK)\TC_ID)

    os.chdir(lib_constants.INPUTPATH)

################################################################################
# Function Name : generate_scripts()
# Parameters    : steps= testcase steps;platform_info,Tc_id,RE_dict
# Functionality : Generates the scripts
# Return Value  : None
################################################################################


def generate_scripts(steps, platform_info, Tc_id, RE_dict, package_type):

    global platform_dir_path
    global dir_path_platform
    global TC_id
    global script_id

    platform_dir_path = lib_constants.OUTPUTPATH + "\\" + dest_path + "\\" + \
        platform_info
    dir_path_platform = os.path.join(lib_constants.OUTPUTPATH + "\\" +
                                     dest_path, TC_id + "-" + platform_info)
    TC_id = Tc_id

    if platform_info == 'NONE':
        dir_path = os.path.join(lib_constants.SOURCEPATH, TC_id)
    else:
        dir_path = os.path.join(lib_constants.OUTPUTPATH + "\\" + dest_path,
                                TC_id)
        flag=[]

        for i in range(len(steps)):
            if "Negative=\"False\"" in steps[i]:
                flag.append("False")
            elif "Negative=\"True\"" in steps[i]:
                flag.append("True")
    step_info.append(len(steps))

    for i in range(len(steps)):
        script_id = TC_id + "-" + str(i+1) + ".py"

        if platform_info in steps[i] and "Platform=\"Yes\"" in steps[i]:
            check(steps[i], platform_info, flag[i], RE_dict, script_id,
                  TC_id, package_type)                                          #checking The Platform Information in the Test Step
            os.chdir(dir_path)
        if platform_info not in steps[i]:
            if platform_info == "NONE":
                os.chdir(dir_path)
                token = ProcessLine(steps[i])                                   # Tokenizing The String
                flag = False
            else:
                if "Platform=\"Yes\"" in steps[i]:
                    continue

                split_token = "Platform=\"No\" >"
                token = ProcessLine(steps[i].split(split_token)[1].strip())     # Tokenizing The String

            if "negative" in token[0].lower():
                token[0] = token[0].split("NEGATIVE:")[1]
                flag = True

            if token[0] == '':
                del token[0]

            ostr = get_original_str()
            keys = list(RE_dict.keys())
            key_match = False

            if True == flag or "True" == flag[i]:
                neg_flag = "True"
            else:
                neg_flag = "False"

            for k in range(len(keys)):
                if re.match(keys[k], ostr, re.I):
                    try:
                        code_generator_call(RE_dict[keys[k]], [token, TC_id,
                                                               script_id,
                                                               package_type,
                                                               neg_flag,
                                                               platform_info])  # Passing the function pointer to Code Generator function for
                    except Exception as e:
                        with open(lib_constants.PARSERLOG, "a") as file_append:
                            file_append.write("ERROR2: due to %s" % e)          # Test Steps which are not Specific to any platform
                    key_match = True
                    break

            if key_match == False:
                generate_syntaxHandlerError(TC_id, script_id, token)

            try:
                if platform_info == "NONE":
                    if flag == True:
                        remove_negative(script_id)                              # Removing The Negative Tag
                        os.chdir(lib_constants.SOURCEPATH)
                else:
                    if flag[i] == "True":
                        remove_negative(script_id)
            except Exception as e:
                with open(lib_constants.PARSERLOG, "a") as file_append:
                    file_append.write("ERROR: due to %s" % e)

            if platform_info == "NONE":
                pass
            else:
                src_files = os.listdir(dir_path)
                for file_name in src_files:
                    full_file_name = os.path.join(dir_path, file_name)
                    if os.path.isfile(full_file_name):
                        shutil.copy(full_file_name, dir_path_platform)          #Copying the Generated files in platform Specific Folder(Format For Folder : TC_ID-APL/BXT/CNL/KBL)

    if platform_info == "NONE":
        pass
    else:
        ########################################################################
        # Generating Folders Based On the Platforms and generated Scripts
        # Function Name : folder_creation
        # Parameters    :  Platform Information
        # Return Value  : None
        # It will Create Folders based on the Applicable platform
        ########################################################################
        try:
            folder_creation(platform_info)
        except Exception as e:
            with open(lib_constants.PARSERLOG, "a") as file_append:
                file_append.write("ERROR: due to %s" % e)

################################################################################
# Function Name : start_parsing
# Parameters    : arg,file_name,destination
# Functionality : Based on arg 0(txt file) or 1(zip package) it will
#                 parse the steps
# Return Value  : steps,platform_info,TC_id
################################################################################


def start_parsing(arg, file_name, destination):

    if os.path.exists(lib_constants.OUTPUTPATH) == True:                        # Checking if Output folder exists
        pass
    else:
        os.mkdir(lib_constants.OUTPUTPATH)                                      # Creating Output Folder

    if arg == 1:
        global dest_path
        dest_path = destination

        if os.path.exists(lib_constants.OUTPUTPATH + "\\" + dest_path) == True:
            pass
        else:
            os.mkdir(lib_constants.OUTPUTPATH + "\\" + dest_path)               # Creating The User specific Folder

        try:
            steps, platform_info, TC_id = Parse_xml(file_name, dest_path)
            return steps, platform_info[0], TC_id
        except Exception as e:
            with open(lib_constants.PARSERLOG, "a") as file_append:
                file_append.write("ERROR2: due to %s" % e)
    else:
        try:
            steps, platform_info, TC_id = Parse_txt(file_name)
            return steps, platform_info, TC_id
        except Exception as e:
            with open(lib_constants.PARSERLOG, "a") as file_append:
                file_append.write("ERROR: due to %s" % e)

################################################################################
# Function Name : read_from_Resultfile
# Parameters    : step = Step no
# Functionality : gets the result value for the corresponding step in result.ini
# Return Value  : result value
################################################################################


def read_from_Resultfile(step):

    try:
        file_path = lib_constants.SCRIPTDIR + "\\Results.ini"
        data = []

        if os.path.exists(file_path):
            for line in reversed(open(file_path).readlines()):
                data.append(line.strip())
            flag = False

            for i in range(len(data)):
                if ("[step-" + str(step) + "]") in data[i].lower():             # Comparing the Step Number
                    flag = True

                    if len(data[i-1].split("=")) == 3:
                        return data[i-1].split("=")[2].strip()                  # Returning the Step Value
                    else:
                        return data[i-1].split("=")[1].strip()                  # Returning the Step Value
            if False == flag:
                return "FAIL: Step-" + str(step) + \
                       " is not present in Result.ini"
        else:
            return "FAIL:Result.ini file is not present "
    except:
        return "FAIL: Result.ini file is not present or Step-" + str(step) + \
               " is not present in Result.ini"

################################################################################
# Function Name : read_input()
# Parameters    : arg,file_name='',dest_path=''
# Functionality : Extracts zip file to get xml inputs
# Return Value  : Name of xml/txt file
################################################################################


def read_input(arg, file_name='', destpath=''):

    global dest_path
    dest_path = destpath

    if arg == 1:
        zip_path = lib_constants.INPUTPATH
        file = zip_path + "\\" + file_name
        name = file.split("\\")[-1].strip()

        try:
            zip_name = name.split("\\")[-1].split(".zip")[0].strip()
            with zipfile.ZipFile(lib_constants.INPUTPATH + "\\" + name,
                                 "r") as z:
                z.extractall(lib_constants.INPUTPATH)                           #Extracting zip file and will store in Output folder
        except Exception as e:
            with open(lib_constants.PARSERLOG, "a") as file_append:
                file_append.write("ERROR: due to %s\n" % e)

        xml_files = glob.glob(lib_constants.INPUTPATH + "\\" + zip_name +
                              "\\CSS-IVE-*.xml")

        if os.path.exists(lib_constants.SYNTAXLOG) == True:
            os.remove(lib_constants.SYNTAXLOG)                                  #Reading the names of the extracted xml files
        return xml_files
    else:
        txt_files = glob.glob(lib_constants.INPUTPATH + "\\*.txt")              #Reading the name of the Text files
        return txt_files

################################################################################
# Function Name : getCurrentStepNo()
# Parameters    : script id
# Functionality : Gets current step number from name of the py file
# Return Value  : returns the current script number
################################################################################


def getcurrentstepno(script_id):

    step_no = script_id.split("\\")                                             #splits the string with "\\"
    CurrentStepNo = step_no[1].split("-")[3]                                    #extracts the step number

    if ".py" in CurrentStepNo:
        CurrentStepNo = CurrentStepNo.split(".py")[0]                           #splits the string with ".py" and extracts the 0th element of the list after splitting

    return int(CurrentStepNo)                                                   #returns the current step number

################################################################################
# Function Name : configtagvariable()
# Parameters    : config entry like config-tag-value
# Functionality : Reads from config and returns the result
# Return Value  : Returns the value after reading from config
################################################################################


def configtagvariable(step):

    step = str.upper(step)                                                   #capitalise the string
    token7 = step.split("-", 3)                                                 #splits string on base of "-"
    tag = token7[1]
    value = token7[2]
    temp = ReadConfig(tag, value)                                               #reads from config
    if "FAIL" in temp:
        return False
    else:
        return temp                                                             #returns the string present in config after extracting

################################################################################
# Function Name : Run_Compare_Images()
# Parameters    : image 1 . image 2 , test case number, script number
# Functionality : Compare image
# Return Value  : Returns true and false
################################################################################


def Run_Compare_Images(Image1, Image2,test_case_id,script_id):

    import time
    import lib_constants
    import subprocess
    import library

    Im1_pix = ""
    Im2_pix = ""
    Im_per = ""
    result = ""

    z = os.path.join(lib_constants.TOOLPATH, 'pixel.exe')                       #go to tools path and save pixel.exe path

    w = (z +  " " + Image1 + " " + Image2)                                      #compare cmd with images path

    os.chdir(lib_constants.TOOLPATH)                                            #change to tool directory
    result = subprocess.Popen(w)                                                #use subprocess to run the command
    time.sleep(15)                                                              #sleep for 15seconds

    if result != None:                                                          # if result is not none
        library.write_log(lib_constants.LOG_INFO, "INFO: Comparing Images "
                          "Successful. Log File Created.", test_case_id,
                          script_id)                                            #success
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "FAIL: Comparing Images "
                          "Unsuccessful.", test_case_id, script_id)
        return False

################################################################################
# Function Name : extract_parameter_from_token
# Parameters    : token[entire grammar token list],start_token,end_token
# Return Value  : returns the parameter as single variable
# Purpose       : to get the parameter from the grammar
################################################################################


def extract_parameter_from_token(token, start_token, end_token, TBD=None,
                                 TBD2=None):

    str = ""
    start_pos = 0                                                               # Declaring empty string
    end_pos = 0

    for i in range(len(token)):                                                 # looping to identify within the length of token
        if token[i] == start_token:                                             # assigning start token to one value
            start_pos = i+1                                                     # incrementing the token
        else:
            pass

        if end_token != "":                                                     # checking if the end token is not empty
            if token[i] == end_token:                                           # checking the value of token assigned is equal as end token
                end_pos = i
        else:
            end_pos = len(token)

    for val in range(start_pos, end_pos):                                       # checking for range of start and end value
        str = str + " " + token[val]                                            # appending the string

    return str.strip(' '), end_pos                                              # returns the value

################################################################################
# Function Name : parse_variable
# Parameters    : token,testcase id, script id
# Functionality : It will parse the config and step variable
# Return Value  : returns the value
################################################################################


def parse_variable(token, tc_id, script_id):

    if re.search("Config*", token, re.IGNORECASE):                              #Checking For Config
        configvalue = configtagvariable(token)                                  #Reading Config Value
        if configvalue:
            return configvalue
        else:
            return False
    elif re.search("Step+", token, re.IGNORECASE):                              #Checking For Step
        stepnum = None

        try:
            stepnum = token.split()[1]
        except:
            return False

        stepvalue = read_from_Resultfile(stepnum)                                 #Reading Step Value
        if stepvalue:
            return stepvalue
        else:
            return False
    else:
        return token

################################################################################
# Function Name : filechangedir
# Parameters    : path
# Functionality : it will change the directory to the given path
# Return Value  : changes the directory
################################################################################


def filechangedir(path):                                                        # function for changing the directory
    os.chdir(path)                                                              # EX: filechangedir("C:\Tests")

################################################################################
# Function Name : check_file
# Parameters : filepath
# Functionality: check for the file exist or not
# Return Value : True if exists, else False
################################################################################


def check_file(filepath):
    if os.path.exists(filepath):                                                #Checking whether path exists or not
        size = int(os.stat(filepath).st_size)
        if 0 == size:
            return False
        else:
            return True

################################################################################
# Function Name : is_installed
# Parameters    : installed_path
# Functionality : checks if application is installed or not
# Return Value  : True if installed or return False
################################################################################


def is_installed(installed_path):

    if os.path.exists(installed_path):
        return True
    else:
        return False

################################################################################
# Function Name : config_check
# Parameters    : config_var,test_case_id, script_id , loglevel and tbd
# Return Value  : Value on success, False on failure
# Functionality : to read and check the config value
################################################################################


def config_check(config_var, test_case_id, script_id, loglevel, tbd):

    if "CONFIG-" in config_var:
        (config_var, section, key) = config_var.split("-")
        config_var = ReadConfig(section, key)                                   # getting the value from config

        if "FAIL:" in config_var:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "Entry is not updated", test_case_id, script_id,
                              "None", "None", loglevel, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config Entry "
                              "Found for %s Section and %s Key"
                              % (str(section), str(key)), test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return str(config_var)
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Given Input Doesn't "
                          "Contain Config Entry", test_case_id, script_id,
                          "none", "none", loglevel, tbd)
        return str(config_var)

################################################################################
# Function Name : execute_with_command
# Parameters    : command, tc_id, script_id, target_os, tool, log_level, tbd,
#                 background
# Functionality : executes given command using Popen
# Return Value  : Tuple contains standard output, input and return value
################################################################################


def execute_with_command(command, tc_id, script_id, tool, log_level="ALL",
                         tbd="None", background=False, shell_status=False):

    try:
        start = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=shell_status,
                                   stdin=subprocess.PIPE)

        if not background:
            stdout, stderr = process.communicate()
            stop = time.time()
            library.write_log(lib_constants.LOG_INFO, "INFO: Process took "
                              "%.02f seconds" % (stop - start), tc_id,
                              script_id, tool, "None", log_level, tbd)

            returncode = int(process.returncode)
            stdout, stderr = list(map(decode, (stdout, stderr)))
            execution_result = result_tuple(returncode, stdout, stderr)
            return execution_result

        library.write_log(lib_constants.LOG_INFO, "INFO: Command Execution "
                          "Started", tc_id, script_id, tool, "None", log_level,
                          tbd)
        return process
    except Exception as ex:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Exception while "
                          "executing command:%s" % ex, tc_id, script_id, tool,
                          "None", log_level, tbd)
        return False


################################################################################
# Function Name : result_tuple
# Parameters : return_code, stdout, stderr
# Functionality: creates a tuple containing results of the executed command
# Return Value : (Tuple)contains standard output, input and return value
################################################################################


def result_tuple(return_code, stdout, stderr):
    result = namedtuple('result', 'return_code stdout stderr')
    return result(return_code, stdout, stderr)



################################################################################
# Function Name : decode
# Parameters : text
# Functionality: decodes execution results
# Return Value : (String) decoded result
################################################################################


def decode(text):
    if not isinstance(text, str):
        text = text.decode(encoding="utf-8")
    return text

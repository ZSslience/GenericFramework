#!/usr/bin/env python
# -*- coding: latin-1 -*-

############################General Python Imports #############################
import re
import time
import sys
import subprocess
import os
########################### Local Imports ######################################
import library
from lib_constants import PROGRAMFILES
from lib_constants import EPCSLOG
from lib_constants import Epcsdir
from lib_constants import workingdir
from lib_constants import BiosDefault
from lib_constants import SCRIPTDIR
################################################################################
#  Function       :   updatebios()
#  Parameters     :	  QuestoUpdate = Question ID which has to be updated in BIOS
#  valuetoUpdate  :   value to be updated to the specific question .Ex: 00 or 01
#  Description    :   This function makes Bios changes if it is not updated.
#  Return         :	  returns true if it updates bios or returns False
################################################################################
def updatebios(stringtoupdate, valuetoUpdate,\
               TC_ID, script_id,specific="",log_level= "ALL",tbd = None,req_line=None):
    os.chdir(Epcsdir)
    if stringtoupdate == "// Max DeepCState":                                   # declaring a bios string to the variable
        if checkforstring(stringtoupdate,TC_ID, script_id, EPCSLOG):            # this function call reads the string and returns if it is present in EPCS Log
            stringtoupdate == "// Max DeepCState"
        else:
            stringtoupdate = "// Max C7 State"
    if stringtoupdate == "// Max C7 State":
        if checkforstring(stringtoupdate, TC_ID, script_id, EPCSLOG):
            stringtoupdate == "// Max C7 State"
        else:
            stringtoupdate = "// Max DeepCState"
    if specific:
        QuestoUpdate = __get_spec_qID(stringtoupdate, specific)            # for any specific bios string in specific section it updates using unique Question id
    else:                                                                       # from the EPCSLOG
        QuestoUpdate = getquestionid(stringtoupdate,\
                                          EPCSLOG,TC_ID, script_id,None,None,req_line)
    try:
        command = "BIOSConf.exe updateq " + QuestoUpdate + " " + valuetoUpdate # EPCS COmmand for updating the string in BIOS
        Proc = subprocess.Popen(command, stdout=subprocess.PIPE,\
                                stderr=subprocess.PIPE)                         # EPCS command to update BIOS string is executed using Subprocess
        Proc.communicate()                                                      # Subprocess output
        output = Proc.returncode
        time.sleep(2)
################################################################################
        command_verify = "BIOSConf.exe verifyq " + QuestoUpdate + " " + valuetoUpdate # EPCS COmmand for updating the string in BIOS
        Proc_verify = subprocess.Popen(command_verify, stdout=subprocess.PIPE,\
                                stderr=subprocess.PIPE)                         # EPCS command to update BIOS string is executed using Subprocess
        Proc_verify.communicate()                                                      # Subprocess output
        output = Proc_verify.returncode
        time.sleep(2)
    except TypeError:
        output = 1
    if not output:                                                              # checking for the condition, if it doean not returns the output
        options = get_options(stringtoupdate, TC_ID, script_id,\
                                   specific, True)                              # It gets the options available in the BIOS for the particular bios string
        invert = [k for k, v in options.items() if v == valuetoUpdate]
        try:
            os.chdir(SCRIPTDIR)
            library.write_log(1, "INFO: %s "
                                 "updated to %s through BIOSConf tool"%
                              (stringtoupdate, valuetoUpdate), TC_ID, script_id,
                              "biosconf","none",log_level,tbd)
        except IndexError:
            os.chdir(SCRIPTDIR)
            library.write_log(3, "ERROR: Failed to update %s "
            "updated to %s through BIOSConf tool"%(stringtoupdate, valuetoUpdate),\
                              TC_ID, script_id,"biosconf","none",log_level,tbd)
        time.sleep(1)
        return True
    else:
        os.chdir(SCRIPTDIR)
        library.write_log(4, "ERROR: Not able to update %s through BIOSConf tool"
                          %stringtoupdate, TC_ID, script_id,"biosconf",
                          "none",log_level,tbd)                                # Exception error is written to log without
        time.sleep(1)
        return False

################################################################################
#   Function     : 	readbios($logfile)
#   Parameters   :  logfile = log file Name
#   Description  :	This function Reads Bios
#   Return       :	returns true if it Read bios
#                   returns false if it fails to read
################################################################################
def readbios(logfile,TC_ID, script_id, log_level= "ALL", tbd = "none"):
    os.chdir(Epcsdir)                                                           # Changing directory to EPCS Directory
    if os.path.isfile(logfile):                                                 # if old log file is present in the EPCS Tool location
        os.remove(logfile)                                                      # It will remove the old EPCS Logs
    time.sleep(4)
    command = "BIOSConf.exe read " + logfile                                 # EPCS Command for reading the BIOS using EPCSTool
    Read = subprocess.Popen\
        ( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE )             # Executing the EPCS command for reading bios using subprocess
    Read.communicate()                                                          # gets the subprocess output
    time.sleep(4)
    if not Read.returncode:                                                     # checks if return code is True from the subprocess output
        with open('epcs_log.txt', 'r') as f_:
            data=f_.readlines()
        with open('epcs_log.txt', 'w') as f_:
            for i in range(len(data)):
                f_.write(data[i].replace("\xae","(R)"))
        os.chdir(workingdir)
        time.sleep(2)
        return True                                                             # returns True if the Read BIOS Command is executed successfully
    else:
        os.chdir(SCRIPTDIR)
        library.write_log(4,"FAIL: Failed to Read Bios",TC_ID,script_id,
                          "biosconf","none",log_level,tbd)
        time.sleep(2)
        return False
################################################################################
#   Function    : getquestionid(string,$logfile)
#   Parameters  : var=variable name and logfile = log file Name
#   Description : This function Reads the Question ID part
#   string      : Is a variable name returns false if it fails to read
################################################################################
def getquestionid(string, logfile, \
                  TC_ID, script_id, log_level= "ALL", tbd = None,line_to_check=None):
    os.chdir(Epcsdir)                                                      # Changing directory to EPCS Directory for reading the log
    EPCSLOG = logfile                                                           # assigning the EPCS log file to a variable named EPCSLOG
    #line_to_check=line_to_check.strip()
    with open(EPCSLOG, 'r') as handle:                                          # Opening the EPCSLog in read mode
        found = False                                                           # declaring the value
        for index, line in enumerate(handle, 1):                                # reading the lines of the log file
            if None == line_to_check:
                if "// Q".lower() in line.lower():
                    line = line.split("// Q")[1].strip()
                if line.upper().rstrip().endswith(string.upper().strip()) \
                        and "form:" not in line.lower():
                    
                    lines = line.split('//')                                    # Splitting the lines based on the '//'
                    pop_items = lines.pop()                                     # removing the end spaces
                    sline = "".join(lines)                                      # joins the lines that is returned
                    RemoveFirstLast = " ".join(sline.split()[1:-1])             # splits the spaces and takes the required string
                    return RemoveFirstLast                                      # Returns the Question iD of the string in BIOS
            else:
                if "// Q".lower() in line.lower():
                    line = line.split("// Q")[1].strip()
                if line.upper().rstrip().endswith(string.upper().strip()) \
                        and "form:" not in line.lower() and line.lower() == line_to_check.lower():
                
                        lines = line.split('//')                                # Splitting the lines based on the '//'
                        pop_items = lines.pop()                                 # removing the end spaces
                        sline = "".join(lines)                                  # joins the lines that is returned
                        RemoveFirstLast = " ".join(sline.split()[1:-1])         # splits the spaces and takes the required string
                        return RemoveFirstLast                                  # Returns the Question iD of the string in BIOS
    return False                                                                # returns False if fails to get the question ID
################################################################################
#  Function    :  CheckForOption(string,val,$logfile)
#  Parameters  :  var= variable name, value = status
#                 and logfile = log file Name
#  Description :  This function Reads Bios
#  Return      :  returns true if it Read bios
#                 returns false if it fails to read
################################################################################
def checkforoption(string, val, TC_ID, script_id, logfile=EPCSLOG, \
                   specific="", log_level= "ALL", tbd = None):
    os.chdir(Epcsdir)                                                           # Changing directory to EPCS Directory to access the EPCSLOG File
    if string == "// Max DeepCState":
        if checkforstring(string, TC_ID, script_id,logfile):                    # checking for the String section
            string == "// Max DeepCState"
        else:
            string = "// Max C7 State"
    if string == "// Max C7 State":                                             # checking for the String section
        if checkforstring(string, TC_ID, script_id, logfile):
            string == "// Max C7 State"
        else:
            string = "// Max DeepCState"
    if specific:                                                                # checking if string comes under specific section where the string might be repeated
        qns = __get_spec_qID(string, specific)                                  # gets the question id for the specific bios string
    else:
        qns = getquestionid(string, logfile,TC_ID, script_id)                   # if not specific then it just gets the question id of the bios string
    try:
        totalid = " Q " + qns + " " + val                                       # EPCS Command for specific
        newstring = totalid.lstrip()
        with open(logfile) as inf:                                              # Opens a logfile
            for line in inf:
                if qns.lower() in line.lower():                                 # checks for the question id
                    lines = line.split('//')                                    # splits the lines based on '//'
                    pop_items = lines.pop()                                     # removes the extra spaces from end
                    sline = "".join(lines)
                    RemoveFirstLast = " ".join(sline.split()[1:-1])
                    stringval = sline.strip()
                    if newstring.upper() == stringval.upper():                  # compares the two strings are equal
                        options = get_options(string,TC_ID,\
                                                   script_id, specific, True)   # it gets the option is available in EPCS Log
                        invert = [k for k, v in options.items() if v == val]
                        try:
                            os.chdir(SCRIPTDIR)
                            library.write_log(1,"INFO: %s"
                                                " is set to %s in BIOS using BIOSConf Tool"
                                              % (string, invert[0]),
                                              TC_ID,script_id,"biosconf",
                                              "none",log_level,tbd)            # writing the result to the log

                        except IndexError:
                            os.chdir(SCRIPTDIR)
                            library.write_log(3,"ERROR: :%s is NOT set "
                                                "to %s in BIOS" % (string, val),
                                              TC_ID,script_id,"biosconf","none",
                                              log_level,tbd)                  # writing the Error to the log

                        time.sleep(1)
                        return True                                             # returns true if option is available in

                    else:
                        options = get_options\
                            (string,TC_ID, script_id, specific, True)
                        invert = [k for k, v in options.items() if v == val]    # gets the return value
                        try:
                            os.chdir(SCRIPTDIR)
                            library.write_log(1,"INFO: Library"
                                                " information:%s not set "
                                                "to %s in BIOS"%(string, invert[0]),
                                              TC_ID,script_id,"biosconf","none",
                                              log_level,tbd)                   # write the information to the log

                        except IndexError:
                            os.chdir(SCRIPTDIR)
                            library.write_log(1,"EPCS Library information: %s"
                             "not set to %s in BIOS" %(string, val),TC_ID,script_id,"biosconf","none",log_level,tbd)

                        time.sleep(1)
                        return False
    except TypeError:
        os.chdir(SCRIPTDIR)
        library.write_log(1,"ERROR: Required string not found in BIOS : "
        "%s" %string,TC_ID,script_id,"biosconf","none",log_level,tbd)                                            # Exception error is written to the log file
        sys.exit(1)
        #return False
################################################################################
#     Function    : checkforstring(string,val,$logfile)
#     Parameters  : var= variable name, value = status, TC_ID = test case id,\
#                   script_id logfile = log file Name
#     Description :	This function Reads Bios
#     Return      :	returns true if it Read bios
#                   returns false if it fails to read
################################################################################
def checkforstring(str12, TC_ID, script_id, logfile=EPCSLOG, specific="",\
                   log_level= "ALL", tbd = None):
    os.chdir(Epcsdir)                                                           # It changes directory to EPCS directory for reading the Log file
    if specific:
        bSpecific = False                                                       # checks if the given bios string is specific and return True
    else:
        bSpecific = True                                                        # returns False if bios string is not specific
    str12=str12.strip()
    with open(logfile) as lines:
        for str1 in lines:                                                      # read the lines of the log file
            if not bSpecific:                                                   # checks if the string is not repeated in the log file
                if str1.rstrip().endswith(specific):                            # strips the string
                    bSpecific = True                                            # True  is assigned to the variable
            if bSpecific:
                if str12.lower() in str1.lower():                                 # if the specific condition is true then chekcks for the string is existing
                    return True                                                 # returns True if the bios string given is available in the EPCSLOG
    return False                                                                # returns False if fail to find the string
################################################################################
#     Function    :   checkbiosoptions(BiosOption, Choices,TC_ID, script_id,)
#     Parameters  :   BiosOption= Bios String, Choise(list) = status, \
#                     TC_ID = test case id, script_id = script id
#     Description :	  This function check for options(Enable/Disable - \
#                     what ever the options
#                     Given in the list) are available in BIOS
#     Return      :	returns true if it all the options are available
#                     returns false if options are not available
################################################################################
def checkbiosoptions(BiosOption, Choices, TC_ID, script_id,\
                     specific="", log_level= "ALL", tbd = None):
    os.chdir(Epcsdir)                                                           # changes directory for reading the EPCSLOG
    BiosOptionCount = 0
    qid_re = re.compile('Q(\s+\d+)*')                                           # re for getiting the question id
    if specific:
        bSpecific = False                                                       # if bios option is repeated multiple times False is assigned to a variable
    else:
        bSpecific = True                                                        # if bios option is not repeated then True is assigned to a variable
    with open(EPCSLOG, 'r') as handle:
        lines = handle.readlines()                                              # opens the log and reads the lines of the log
    for index, line in enumerate(lines):
        if not bSpecific:
            if (line.rstrip().lower()).endswith(specific.lower()):              # strips the extra spaces of the bios option and assigned true to the variable if the bios option is preaent
                bSpecific = True
        if bSpecific:
            if (line.rstrip().lower()).endswith(BiosOption.lower()) :
                if ((line.rstrip().lower()).split('//')[1].strip(' ')
                        == BiosOption.lower().strip(' ')):
                    count = index + 1
                    while not qid_re.search(lines[count]):
                        count += 1
                    for Choice in Choices:
                        Choice = ' ' + Choice
                        for item in lines[index+1:count]:
                            if Choice.lower().strip(' ') in item.lower():
                                BiosOptionCount += 1
                                break
                    break
    if BiosOptionCount == len(Choices):                                         # checks if the bios option is same as the number of choices available
        return True                                                             # returns True if all the options available in the bios log
    else:
        os.chdir(SCRIPTDIR)
        library.write_log(1,"INFO: All the option are not available under "
        "%s" %BiosOption,TC_ID,script_id,"biosconf","none",log_level,tbd)
        return False                                                            # returns False if all the available options
################################################################################
#  Function Name : getcurrentoption()
#  Parameters    : string = bios string; logfile = EPCS Log file
#                 script_id = script id; TC_id = testcase_id
#  Functionality : gets current option in bios for the given bios option
#  return        : Bios option value
################################################################################
def getcurrentoption(string, logfile,TC_ID="", \
                     script_id="",log_level= "ALL", tbd = None):
    os.chdir(Epcsdir)
    qns = getquestionid(string, logfile,TC_ID, script_id)                       # gets the question id for the specific option required
    with open(logfile, 'r') as inf:
        for line in inf:                                                        # opens the logfile adn reads the line
            if qns.lower() in line.lower():                                     # question id is present in the line
                Value = re.search('ONE_OF\s*(\w+)\s*//', line)\
                        or re.search('NUMERIC\s*(\w+)\s*//', line) \
                                                               \
                        or re.search('CHECKBOX\s*(\w+)\s*//', line)             # checks if otion is 1 among the 3 values eithe 'ONE_OF' of 'NUMERIC' or 'CHECKBOX'
                if Value:
                    return Value.group(1)                                       # if the option is available the returns the current bios value for the option given
                else:
                    return
################################################################################
#    Function Name   : 	GetCurrentOption_New()
#    Parameters      :  (string) = Bios String for which the options and \
#                       values has to be found
#                       TC_ID  : test case id; logfile: EPCSLOG file
#                       script_id : script id
#    Functionality   :  current bios option in identified
#    Return          :  BIOS current Value
################################################################################
def getcurrentoption_new(string, logfile,TC_ID="",\
                         script_id="", log_level= "ALL", tbd = None,line_to_chk=None):
    os.chdir(Epcsdir)
    string=string.strip()
    qns = getquestionid(string, logfile,TC_ID, script_id,log_level,tbd,line_to_chk)
    with open(logfile, 'r') as inf:
        for line in inf:
            if "// Q".lower() in line.lower():
                line = line.split("// Q")[1].strip()
            if line_to_chk == None:
                if qns in line:
                    Value = re.search('ONE_OF\s*(\w+)\s*//', line,re.IGNORECASE) \
                            or re.search('NUMERIC\s*(\w+)\s*//', line,re.IGNORECASE) \
                                                                    or \
                            re.search('CHECKBOX\s*(\w+)\s*//', line,re.IGNORECASE)                # checks if otion is 1 among the 3 values eithe 'ONE_OF' of 'NUMERIC' or 'CHECKBOX'
                    break
            else:
                if line_to_chk.lower() in line.lower() and qns in line:
                    Value = re.search('ONE_OF\s*(\w+)\s*//', line,re.IGNORECASE) \
                            or re.search('NUMERIC\s*(\w+)\s*//', line,re.IGNORECASE) \
                                                                or \
                            re.search('CHECKBOX\s*(\w+)\s*//', line,re.IGNORECASE)                # checks if otion is 1 among the 3 values eithe 'ONE_OF' of 'NUMERIC' or 'CHECKBOX'
                    break
        if Value:
            
            return Value.group(1),str(qns)                            # if the option is available the returns the current bios value for the option given
        else:
            return 
################################################################################
#    Function Name  : 	ResetBiosChanges()
#    Parameters     :   (string) = Bios String for which the options \
#                       and values has to be found
#                       TC_ID  : test case id
#                       script_id : script id
#    Functionality  :   Reverts back the bios changes done to default
#    Return         :   True
################################################################################
def ResetBiosChanges(string,TC_ID="", script_id="", log_level= "ALL", tbd = None):
    DefaultSetting = getcurrentoption(string, \
                                           BiosDefault,TC_ID,script_id)         # gets the default value of bios string
    CurrentSetting = getcurrentoption(string, EPCSLOG,TC_ID, script_id)         # gets the current value of the bios string
    if CurrentSetting and DefaultSetting:                                       # checks if the default value and the current value is same
        if DefaultSetting == CurrentSetting:                                    # if the default value and the current value is same returns True
            return True
        else:
            return updatebios(string, DefaultSetting,TC_ID, script_id)          # if the default value is not same as the current value then if updates it to the default value
    else:
        return
################################################################################
#    Function Name   : 	get_options(bios_option, TC_ID, script_id, specefic="",\
#                       internal=False)
#    Parameters      :  get_options(string) = Bios String for which the options\
#                       and values has to be  found
#                       TC_ID  : test case id
#                       script_id : script id
#                       specific: Option will be checked under this BIOS menu
#    Return          :  Bios Option
#    Functionality   :  Outputs the available option under the particular bios
#                       section
################################################################################
def get_options(bios_option, TC_ID, script_id, specefic="",\
                internal=False, log_level = "ALL",tbd = None,q_id_to_check=None):
    
    os.chdir(Epcsdir)
    BiosOption = dict()                                                         # empty dictionary is assigned to the variable
    flag = False                                                                # flag initialisation
    qid_re = re.compile('Q(\s+\d+)*')                                           # gets the re question id
    bios_option=bios_option.strip()
    with open(EPCSLOG, 'r') as handle:
        lines = handle.readlines()                                              # reads the lines of the log file
    for index, line in enumerate(lines):
        #line=line.strip()
        if specefic:                                                            # checkd for the specific bios option is availabe
            if line.rstrip().endswith(specefic):                                # strips the line if the option is specific
                flag = True                                                     # True is assigned to the flag
                continue
        else:
            flag = True
        if flag:
            if None == q_id_to_check:
                if line.upper().rstrip().endswith(bios_option.upper()) \
                        and "form:" not in line.lower():
                    count = index + 1
                    while not qid_re.search(lines[count]):                          # if flag is True the gets the question id for all the lines available
                        count += 1
                    for options in lines[index+1:count]:
                        try:
                            value, name = options.split("=")                        # if the option is present then it splits it with the '='
                            value = value[2:].strip()
                            name = name.strip()
                            BiosOption[name] = value
                        except ValueError:
                            pass
            else:
                if line.upper().rstrip().endswith(bios_option.upper()) \
                        and "form:" not in line.lower() and q_id_to_check.lower() in line.lower():
                    count = index + 1
                    while not qid_re.search(lines[count]):                          # if flag is True the gets the question id for all the lines available
                        count += 1
                    for options in lines[index+1:count]:
                        try:
                            value, name = options.split("=")                        # if the option is present then it splits it with the '='
                            value = value[2:].strip()
                            name = name.strip()
                            BiosOption[name] = value
                        except ValueError:
                            pass

    if BiosOption:
        if internal:
            return BiosOption                                                   # returns the Bios available for the Bios string
        os.chdir(SCRIPTDIR)
        library.write_log(1,'INFO: Following options are available under %s'
                          %bios_option,TC_ID, script_id,"biosconf","none",log_level,tbd)
        for key, values in BiosOption.items():
            os.chdir(SCRIPTDIR)
            library.write_log(1,"INFO: \t%s : %s" % (key, values),
                              TC_ID, script_id,"biosconf","none",log_level,tbd)
        return BiosOption
################################################################################
#  Function Name :  __get_spec_qID()
#  Parameter     :  stringtoupdate= Bios Option to be updated; \
#                   specific = Specific Bios form/feature
#  Functionality :  Get the question id of any bios option \
#                   under a specific BIOS feature
#  Return        :  Question Id for the Bios Option
################################################################################
def __get_spec_qID(stringtoupdate, specific,log_level= "ALL", tbd = None):
    flag = False
    os.chdir(Epcsdir)                                                           # changing directory to EPCS to read the log file
    with open(EPCSLOG) as handle:
        for line in handle:
            if line.upper().rstrip().endswith(specific.upper()):
                flag = True                                                     # returns true if the option is availabele in the log
            if flag:
                if line.upper().rstrip().endswith(stringtoupdate.upper()):                      # strips the option
                    lines = line.split('//')                                    # splits it with the '//'
                    lines.pop()
                    sline = "".join(lines)
                    RemoveFirstLast = " ".join(sline.split()[1:-1])
                    return RemoveFirstLast                                      # returns the question id for the specific bios options which are repeated more then once
################################################################################

# Example to call the functions for EPCS:::

#_EPCS.CheckBiosOptions("// Fast Boot", ["Disabled", "Enabled"],\
#  "// Form: Memory Configuration")
#_EPCS.readbios(EPCSLOG)
# print _EPCS.CheckBiosOptions("// DVMT Pre-Allocated",\
# print _EPCS.get_options("// DVMT Pre-Allocated", "// Form: Graphics Configuration")
# print _EPCS.get_spec_qID("// DMI Link ASPM Control", "// PCI Express Configuration")
# print _EPCS.get_spec_qID("// DMI Link ASPM Control", "// DMI/OPI Configuration")
#_EPCS.CheckForOption("// Memory Voltage", "00", EPCSLOG)
#_EPCS.updatebios('// C states', '00')
# test = _EPCS.get_options("// Low Power S0 Idle Capability", internal=True)
#_EPCS.ResetBiosChanges('// DPTF')

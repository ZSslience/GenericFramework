############################General Python Imports##############################
import os
import sys
import glob
import codecs
from win32api import GetSystemMetrics
import subprocess
############################Local Python Imports################################
import utils
import library
import lib_constants
################################################################################
# Function Name : lib_verify_display_properties
# Parameters    : test_case_id-test case ID, script_id  - script ID,
#                 action - compare
# Purpose       : Verifies display properties for landscape and resolution
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : Verify Display for <display_device> {with <display_property>
################################################################################


def lib_verify_display_properties(test_case_id, script_id, token,
                                  log_level="ALL", tbd=None):

    test_case_id = test_case_id
    script_id = script_id
    token_option = token[5]                                                     #store token5
    token_operator = token[6]                                                   #store token6
    resolutionx = " "
    resolutiony = " "
    ori = " "
    global res
    try:
        resolutionx = GetSystemMetrics(0)
        resolutiony = GetSystemMetrics(1)

        if (resolutionx > resolutiony):
            ori = "landscape"                                                   #if x > y  orientation is landscape

        else:
            ori = "portrait"                                                    # else in portrait

        if "RESOLUTION" == token_option:                                        #if resolution in token4
            if "config" in token_operator.lower():                              #if resolution taken from config.ini
                res_ind = token_operator.split("-")
                token_operator = utils.ReadConfig(res_ind[1], res_ind[2])
            if "X" in token_operator:
                res = token_operator.split("X")                                 #split with "X"
            elif "x" in token_operator:
                res = token_operator.split("x")
            elif "*" in token_operator:
                res = token_operator.split("*")

            if(int(res[0]) == int(resolutionx) and
                        int(res[1]) == int(resolutiony)):                       #verify the resolution with the given values and perform as per results
                library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                'resolution ' + token_operator +' are matching', test_case_id ,
                script_id, "None", "None", log_level, tbd)
                return True

            else:
                library.write_log(lib_constants.LOG_INFO, 'INFO : Wrong input'  #wrong input values
                'for display resolution '+token_operator,  test_case_id,
                script_id, "None", "None", log_level, tbd)
                return False

        elif "ORIENTATION" == token_option:
            library.write_log(lib_constants.LOG_INFO, "INFO:Verifying display "
            "for Orientation " + token_operator, test_case_id, script_id,
            "None", "None", log_level, tbd)
            if "90" == token_operator:                                          #check for 90 in input token
                display_orientation = "PORTRAIT"                                #sets display_configuration to portrait

                if ori.upper() == display_orientation:
                    library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                    'is in Portrait mode', test_case_id, script_id, "None",
                    "None", log_level , tbd)
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, 'INFO :Display'
                    ' is not in Portrait mode',  test_case_id, script_id,
                    "None", "None", log_level, tbd)
                    return False
            elif "180" == token_operator:                                       #check for 180 in token 6
                display_orientation = "LANDSCAPE"                               #set token6 to landscape

                if display_orientation == ori.upper():                          #if token6 is equal to ori
                    library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                    'is in Landscape mode', test_case_id , script_id , "None",
                    "None", log_level, tbd)
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, 'INFO : Display'
                    ' is not in Landscape mode',  test_case_id, script_id,
                    "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_INFO, 'INFO :Wrong'
                'input values for orientation is given ', test_case_id ,
                script_id ,"None","None", log_level, tbd)
                return False                                                    #return false

        else:
            library.write_log(lib_constants.LOG_INFO, 'INFO : Wrong'
            ' input values for display property is given',  test_case_id ,
            script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : %s " %e,
        test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : lib_verify_display_only
# Parameters    : test_case_id-test case ID, script_id  - script ID,
#                  token - display device
# Purpose       : Verifies display device only
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def lib_verify_display_only(test_case_id, script_id, token, log_level="ALL",
                            tbd=None):

    try:
        if "VGA" in token.upper():
            vga_display_cmd = lib_constants.VGA_DISPLAY_CMD
            result = subprocess.check_output(["powershell.exe",
                                              vga_display_cmd ],
                                             shell=True)                        #get analogue signal by using powershell command
            path =os.path.join(lib_constants.SCRIPTDIR,
                               script_id.replace(".py",".txt"))                 #creating txt file with script name
            log = open(path,'w')
            for data in result:
                log.write(data)                                                 #writing the result data in to file
            log.close()
            flag = False
            with codecs.open(path ,'r',"utf-8") as handle:                      #file operation open file in utf-8 mode and save the texts in handle
                for line in handle:                                             #iterate through the lines
                    if "VideoInputType                : 0" in line:             #if video type is 0 means analogue signal type of display is there
                        flag=True
                        break

            if flag:
                library.write_log(lib_constants.LOG_INFO, 'INFO : '
                            '%s Display is connected'%token, test_case_id,
                            script_id,"None", "None", log_level , tbd)          #if flag is true than it will print pass log
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,'INFO:'
                    '%s Display is not connected'%token,test_case_id,
                    "None","None",log_level,tbd)
                return False                                                    #flag is false, it will printing  false log
        else:
            tool_dir = utils.ReadConfig("DISPLAY", "tooldir")                   #Read the tools directory path from the config and store in tool_dir
            cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")
            if "FAIL:" in [tool_dir, cmd_to_run]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING:Config "
                "valuesunder DISPLAY section are missing", test_case_id,
                script_id,"None", "None",log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO:config values "
                "under DISPLAY section are found", test_case_id, script_id,
                "None","None",log_level, tbd)
            value = 0
            flag = 0
            utils.filechangedir(tool_dir)
            p = os.system(cmd_to_run)                                           #Execute the command to get the display property
            if 0 != p:                                                          #Failed to execute the command
                return False                                                    #return "False"
            else:
                file = glob.glob("DisplayInfo.txt")                             #check for displayinfo.txt in the directory
                if [] == file:                                                  #if file is empty
                    return False                                                #return "false"
                else:
                    utils.filechangedir(tool_dir)                               #change to tools directory where tool is kept
                    with codecs.open("DisplayInfo.txt","r", "utf-8") as handle: #file operation open file in utf-8 mode and save the texts in handle
                        for line in handle:                                     #iterate through the lines
                            if token in line:                                   #verify if display token in line
                                value = 1                                       #change value to 1 from 0 if token is found
                                break                                           #break from the loop

                    if 1 == value:
                        library.write_log(lib_constants.LOG_INFO, 'INFO : '
                        '%s Display is configured'%token, test_case_id,
                        script_id,"None", "None", log_level , tbd)
                        return True                                             #return "True" when display property is found
                    else:
                        library.write_log(lib_constants.LOG_INFO, 'INFO : '
                        '%s Display is not configured'%token, test_case_id,
                        script_id, "None", "None", log_level , tbd)
                        return False                                            #return "False" when display property is not found
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
        test_case_id, script_id, "None", "None", log_level, tbd)
        return False
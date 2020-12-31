__author__ = 'patnaikx'
############################General Python Imports##############################
import os
import re
import sys
import time
import glob
import codecs
import win32api
from win32api import GetSystemMetrics
import subprocess
############################Local Python Imports################################
import utils
import library
import lib_constants
import lib_verify_display_properties
################################################################################
# Function Name : win32_display_set
# Parameters    : width - horizontal resolution, height - vertical resolution,
#                   depth - colorDepth
# Functionality : changes display properties e.g. resolution/colorDepth
# Return Value  : None
################################################################################


def win32_display_set(width=None, height=None, depth=None):                     #code for set display property
    try:
        if width and height and depth:
            mode = win32api.EnumDisplaySettings()                               #EnumDisplaySetting() will take display param input
            mode.PelsWidth = width
            mode.PelsHeight = height
            mode.BitsPerPel = depth

            win32api.ChangeDisplaySettings(mode, 0)                             #change the display setting if depth is defined
        else:
            win32api.ChangeDisplaySettings(None, 0)                             #change display default colorDepth
    except:
        return False
################################################################################
# Function Name : lib_verify_display_with_display_properties
# Parameters    : test_case_id-test case ID, script_id  - script ID,
#                   token - input token
# Functionality : Verifies display with display properties
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : Verify <display type> display with <display feature>
#                   <display feature value>
#################################################################################code for verifying display properties


def verify_display_with_display_properties(token, test_case_id, script_id,
                                                log_level="ALL" , tbd=None):
    token = utils.ProcessLine(token)
    display = token[1]                                                          #store display device type from input token
    token_option = token[4]                                                     #store display property from input token
    token_operator = token[5]                                                   #store property value to be check from input token
    resolutionx = " "
    resolutiony = " "
    ori = " "
    global res
    try:
        if "config" in token_operator.lower():                                  #if resolution value taken from config.ini
            res_ind = token_operator.split("-")
            token_operator = utils.ReadConfig(res_ind[1], res_ind[2])
            if "FAIL:" in token_operator:
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                    "config entry for display property %s is not found under "
                    "tag %s "%(res_ind[1], res_ind[2]),test_case_id,script_id,
                    "None", "None", log_level, tbd)
            else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Config"
                    " entry for display property %s is fetched under tag "
                    "%s"%(res_ind[1], res_ind[2]), test_case_id,
                    script_id, "None", "None", log_level, tbd)
        if "RESOLUTION" == token_option:                                        #store display device type from input token
            if "X" in token_operator:
                res = token_operator.split("X")                                 #split with "X"
            elif "x" in token_operator:
                res = token_operator.split("x")
            elif "*" in token_operator:
                res = token_operator.split("*")
            try:
                win32_display_set(int(res[0]), int(res[1]), 32)                 #calling win32_display_set for resolution change keeping color depth constant
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : "
                "%s " %e,test_case_id, script_id, "None", "None", log_level,
                                  tbd)
                return False

            resolutionx = GetSystemMetrics(0)                                   #set the horizontal resolution value to resolutionx
            resolutiony = GetSystemMetrics(1)                                   #set the Vertical resolution value to resolutiony
            library.write_log(lib_constants.LOG_DEBUG, 'DEBUG : Current '
            'Display resolution is %sX%s'%(resolutionx,resolutiony),
            test_case_id ,script_id,"None", "None", log_level,tbd)              #print current display resolution
            if(int(res[0]) == int(resolutionx) and
                        int(res[1]) == int(resolutiony)):                       #verify the resolution with the given values and perform as per results

                library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                'resolution ' + token_operator +' are matching with input',
                test_case_id ,script_id, "None", "None", log_level, tbd)
                library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                'resolution changed successfully and verified the '
                'display resolution property',test_case_id ,script_id,
                "None", "None", log_level, tbd)
                return True

            else:
                library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                'resolution '+token_operator + 'are not matching with input',
                test_case_id,script_id, "None", "None", log_level, tbd)
                library.write_log(lib_constants.LOG_INFO, 'INFO : Failed to '
                'change display resolution and verification for '
                'display resolution property got failed',test_case_id ,
                script_id, "None", "None", log_level, tbd)
                return False

        elif "ROTATION" == token_option:
            library.write_log(lib_constants.LOG_INFO, "INFO:Verifying display "
                "for Orientation " + token_operator, test_case_id, script_id,
                            "None", "None", log_level, tbd)
            tool_dir = utils.ReadConfig("DISPLAY", "tooldir")                   #Read the tools directory path from the config and store in tool_dir
            if "FAIL:" in tool_dir:
                library.write_log(lib_constants.LOG_INFO, "INFO:config value for "
                "tool_dir is missing under DISPLAY tag", test_case_id,
                script_id, "DISPLAY", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO:config value for "
                "tool_dir is found under DISPLAY tag", test_case_id, script_id,
                "DISPLAY", "None", log_level, tbd)
            list_orientation = []                                               #create a list of display rotation
            if token_operator == "270" or token_operator == "180" or \
                            token_operator == "90":
                list_orientation = [token_operator]                             #if only one rotation given in input append it to rotation list
            elif token_operator.lower() == "all":
                list_orientation = ["90", "180", "270", "0"]                    #for all type of rotation
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Wrong "
                "input for display orientation value ", test_case_id,
                script_id, "DISPLAY", "None", log_level, tbd)
                return False
            try:
                for ori_value in list_orientation:                              # for all type of rotation listed in list_orientation
                    os.chdir(tool_dir)
                    cmd_to_change_ori = "Display.exe /rotate:%s"%ori_value      #command for change the rotation
                    os.system(cmd_to_change_ori)
                    time.sleep(lib_constants.TEN)
                    resolutionx = GetSystemMetrics(0)                           #note down display horizonatal and vertical resolution after rotation
                    resolutiony = GetSystemMetrics(1)
                    if (int(resolutionx) > int(resolutiony)):
                        ori = "landscape"                                       #if x > y  orientation is landscape

                    else:
                        ori = "portrait"                                        #if x < y orientation is portrait
                    library.write_log(lib_constants.LOG_DEBUG, 'DEBUG : Current'
                    'Display orientation/rotation is %s'%ori,
                    test_case_id ,script_id,"None", "None", log_level, tbd)     #print current display orientation

                    if "90" == ori_value or "270" == ori_value:                 #if orientation is 90 or 270 degree
                        if "PORTRAIT" == ori.upper():                           #if display is in PORTRAIT mode
                            library.write_log(lib_constants.LOG_INFO, 'INFO : '
                            'Display is in Portrait mode after rotating '
                            '%s'%ori_value, test_case_id, script_id,
                            "None","None", log_level , tbd)

                        else:
                            library.write_log(lib_constants.LOG_INFO, 'INFO :'
                            'Display is not in Portrait mode',  test_case_id,
                            script_id, "None", "None", log_level, tbd)
                            os.system("Display.exe /rotate:0")                  #make display to default orientation
                            library.write_log(lib_constants.LOG_INFO, 'INFO : '
                            'Failed to rotate display and verification for '
                            'display rotation property got failed',test_case_id,
                            script_id, "None", "None", log_level, tbd)
                            return False
                    elif "180" == ori_value or "0" == ori_value:                #if orientation is 180 or 0 degree
                        if "LANDSCAPE" == ori.upper():                          #if display is in LANDSCAPE mode
                            library.write_log(lib_constants.LOG_INFO, 'INFO : '
                            'Display is in landscape mode', test_case_id,
                            script_id, "DISPLAY","None", log_level , tbd)
                        else:
                            library.write_log(lib_constants.LOG_INFO, 'INFO :'
                            'Display is not in Landscape mode',  test_case_id,
                            script_id, "None", "None", log_level, tbd)
                            os.system("Display.exe /rotate:0")                  #make display to default orientation
                            library.write_log(lib_constants.LOG_INFO, 'INFO : '
                            'Failed to rotate display and verification for '
                            'display rotation property got failed',test_case_id ,
                            script_id, "DISPLAY", "None", log_level, tbd)
                            return False
                    else:
                         library.write_log(lib_constants.LOG_INFO, 'INFO :'
                         'Wrong input for orientation value in display',
                          test_case_id, script_id, "DISPLAY", "None",
                          log_level, tbd)
                         os.system("Display.exe /rotate:0")                     #make display to default orientation
                         return False
                os.system("Display.exe /rotate:0")                              #make display to default orientation
                library.write_log(lib_constants.LOG_INFO, 'INFO : Display '
                'rotate successfully and verified the display '
                'orientation/rotation property',test_case_id ,script_id,
                "DISPLAY", "None", log_level, tbd)
                return True
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : "
                "%s " %e,test_case_id, script_id, "None", "None", log_level,
                                  tbd)
                return False

        elif "COLORDEPTH" == token_option:
            if "BPP" in token_operator.upper():                                 #take only integer value and remove any other string if
                res = int(re.search(r'\d+', token_operator).group())
                res = str(res)                                                  #change integer value to string for concatenate
            else:
                res = str(token_operator)

            try:
                win32_display_set(1280, 1024, int(res))
                time.sleep(lib_constants.TEN)
                cmd_for_primary_dis = lib_constants.PRIMARY_DISPLAY_CMD %res    #power_shell command for primary display to get color depth
                cmd_for_secondary_dis = lib_constants.SECONDARY_DISPLAY_CMD %res#power_shell command for secondary display to get color depth
                result_edp = lib_verify_display_properties.\
                        lib_verify_display_only(test_case_id, script_id, "EDP",
                                                log_level="ALL",tbd=None)       #checking for eDP display availability in sut
                result_hdmi = lib_verify_display_properties.\
                        lib_verify_display_only(test_case_id, script_id, "HDMI",
                                                log_level="ALL", tbd=None)      #checking for HDMI display availability in sut
                if "EDP" == display and result_edp:                             #if display is eDP and eDP is connected
                    cmd = cmd_for_primary_dis
                    library.write_log(lib_constants.LOG_INFO,"INFO: Checking "
                    " color depth for eDP display color depth", test_case_id,
                    script_id, "None","None", log_level, tbd)
                elif "HDMI" == display and result_hdmi and result_edp:          #if display is HDMI and eDP and HDMI both connected
                    cmd = cmd_for_secondary_dis
                    library.write_log(lib_constants.LOG_INFO, "INFO: Checking"
                    " color depth for HDMI display", test_case_id, script_id,
                    "None","None", log_level, tbd)
                elif "HDMI" == display and result_hdmi and not result_edp:      #if display is HDMI and only HDMI is connected
                    cmd = cmd_for_primary_dis
                    library.write_log(lib_constants.LOG_INFO,"INFO: Checking"
                    " color depth for HDMI display", test_case_id, script_id,
                    "None","None", log_level, tbd)

                else:                                                           #if wrong display name given or no display is connected
                    library.write_log(lib_constants.LOG_WARNING, 'INFO : '
                    'Wrong input for display given or check for the '
                    'availability of %s display'%display, test_case_id,
                    script_id, "None", "None", log_level, tbd)
                    return False
                utils.filechangedir(lib_constants.SCRIPTDIR)
                for filename in os.listdir("."):                                #check for filename in directory for nsh

                    if filename.endswith("ps1"):                                #if any nsh file is there unlink the file
                        os.unlink(filename)

                    else:
                        library.write_log(lib_constants.LOG_INFO,"INFO: No old "
                        "Powershell log exists", test_case_id, script_id,
                                  "None","None", log_level, tbd)
                        pass
                myFile=open("psquery.ps1","w")                                  #opening a powershell file
                myFile.write(cmd)                                               #writing command for getting colordepth in psquery.ps1 file
                myFile.close()
                time.sleep(lib_constants.FIVE_SECONDS)                          #sleep for 5 seconds
                new_script_id = script_id.strip(".py")
                log_file = new_script_id + '.txt'
                script_dir = lib_constants.SCRIPTDIR
                log_path = script_dir + "\\" + log_file
                powershell_path = utils.ReadConfig("WIN_POWERSHELL", "PATH")    #Read from powershell the vaue of powershell path
                if "FAIL" in powershell_path:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                    "config entry of powershell_path is not proper ",
                    test_case_id,script_id, "None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Config"
                    " entry of powershell_path is fetched ", test_case_id,
                    script_id, "None", "None", log_level, tbd)
                shell_script = 'psquery.ps1'                                    #shell script should be placed in script directory

                exe_path = os.path.join(lib_constants.SCRIPTDIR, shell_script)
                final_command = 'powershell.exe '+ exe_path + ' > ' + log_path  #concate the commands along with the log path

                try:
                    os.chdir(powershell_path)
                    subprocess.Popen(final_command, shell=True,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)                 #run the command to get the log for color depth

                except Exception as e:
                    os.chdir(lib_constants.SCRIPTDIR)
                    library.write_log(lib_constants.LOG_ERROR, "ERROR:"
                    " Exception occurred due to %s"%e, test_case_id,
                    script_id, "None","None", log_level, tbd)
                    os.chdir(lib_constants.SCRIPTDIR)

                if (os.path.exists(log_path)):                                  #if color depth log file generate
                    file_size = os.path.getsize(log_path)                       #get the size of the log file
                    if 0 == file_size:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Failed to change the colorDepth value to %s"%res,
                        test_case_id, script_id, "None","None", log_level, tbd)
                        library.write_log(lib_constants.LOG_INFO, 'INFO : '
                        'verification for display color-depth property got '
                        'failed',test_case_id ,script_id, "None", "None",
                        log_level,tbd)
                        return False                                            #if colorDepth change not configured
                    else:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Colordepth changed to %s"%res, test_case_id,
                         script_id, "None","None", log_level, tbd)
                        library.write_log(lib_constants.LOG_INFO, 'INFO :  '
                        'Display color-depth property verified successfully',
                        test_case_id ,script_id,"None", "None", log_level, tbd)
                        return True                                             #if colordepth of display change
                else:
                    library.write_log(lib_constants.LOG_FAIL,"FAIL: Color-depth"
                    " log failed to get generate", test_case_id,
                    script_id, "None", "None", log_level, tbd)
                    return False                                                #returns false if failed to run the command for changing display colordepth
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : "
                "%s " %e,test_case_id, script_id, "None", "None", log_level,
                                  tbd)
                return False                                                    #exception handled for display property change


        else:
            library.write_log(lib_constants.LOG_INFO, 'INFO : Wrong'
                ' input values for display property',  test_case_id , script_id,
                "None", "None", log_level, tbd)
            return False                                                        #returns false if any wrong display property given
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : %s " %e,
                test_case_id, script_id, "None", "None", log_level, tbd)
        return False

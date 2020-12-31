__author__ = 'nareshgx\tnaidux'

# #########################General Python Imports##############################
import os
import pyautogui
import re
import subprocess
import time
import _thread
import win32gui
# ###########################Local Python Imports##############################
import lib_constants
import library
import utils



# #############################################################################
# Function Name : winfun
# Parameters    : hwnd and lparam
# Return Value  : to get error window content
# Purpose       : To check error in playback and verify playback
# #############################################################################


def winfun(hwnd, lparam):                                                       # get error window content
    s = win32gui.GetWindowText(hwnd)
    if len(s) > 0:
        # print("winfun, child_hwnd: %d   txt: %s" % (hwnd, s))
        pass
    return 1

################################################################################
# Function Name : create_wmp_regedit
# Parameters    : test_case_id, script_id, log_level and tbd
# Return Value  : return True/ False
# Purpose       : To create bat file to remove welcome screen for 1st time use
###############################################################################


def create_wmp_regedit(test_case_id, script_id, log_level="All", tbd=None):     #create a bat file to skip window media player welcome screen
    set_reg_wmp = lib_constants.SET_REG_EDIT_WMP
    with open("winplayer.bat", "w") as f:
        f.write(set_reg_wmp)

    cmd_exe = subprocess.Popen("winplayer.bat", shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE)#execute bat file in subprocess
    exec_out = cmd_exe.communicate()[0]
    if "successfully" in exec_out:
        library.write_log(lib_constants.LOG_INFO, "INFO: Windows media player "
        "regedit is set to skip welcome screen", test_case_id, script_id,
        "None", "None", log_level, tbd)                                         #writing log info message to the log file
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Windows media "
        "player regedit was not set properly", test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing log warning message to the log file
        return False
###############################################################################
# Function Name : find_app_window_wmp
# Parameters    : app_name, test_case_id, script_id, log_level and tbd
# Return Value  : return True/ False
# Purpose       : to find wmplayer window
###############################################################################


def find_app_window_wmp(app_name, test_case_id, script_id, log_level="All",
                        tbd=None):                                              # find wmplayer application
    hwnd = win32gui.FindWindow(None, app_name)
    if hwnd < 1:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: %s Application "
        "not found"%app_name, test_case_id, script_id, "None", "None",
        log_level, tbd)                                                         #Writing log warning message to the log file
        return False
    else:
        try:
            find_status = win32gui.EnumChildWindows(hwnd, winfun, None)         # if application is found, return the state of application returns if app is playing some file
            return find_status
        except:
            state = win32gui.GetWindowText(hwnd)                                # if application is found, return the state of application
            if state == app_name:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s App found"
                %app_name, test_case_id, script_id, "None", "None", log_level,
                tbd)                                                            #writing log info message to the log file
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                "WARNING: Application not found", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log warning message to the log file
                return False
###############################################################################
# Function Name : play_media_wmp
# Parameters    : cmd_wmp
# Return Value  : none
# Purpose       : To launch wmplayer
###############################################################################


def play_media_wmp(cmd_wmp):                                                    # function to play file in thread
    cmd_exe = subprocess.Popen(cmd_wmp, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    exec_out = cmd_exe.communicate()[0]
###############################################################################
# Function Name : verify_playback
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To verify playback
###############################################################################

def verify_playback(test_case_id, script_id, log_level="All", tbd=None):        # function to verify playback without any error
    find_app = find_app_window_wmp("Windows Media Player", test_case_id,
                                   script_id, log_level, tbd)                   #to find wmplayer application
    if find_app:
        library.write_log(lib_constants.LOG_INFO, "INFO: WMPlayer launched",
        test_case_id, script_id, "None", "None", log_level, tbd)                #writing log info message to the log file
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Playback failed",
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing log warning message to the log file
        return False

###############################################################################
# Function Name : play_file_pdvd
# Parameters    : media_type,test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To launch and verify this is the main function
###############################################################################
def play_file_pdvd(media_type, test_case_id, script_id, log_level="All",
                   tbd=None):
    app_name = "pdvd"
    pdvd_tool_dir = utils.ReadConfig(app_name, "tooldir")                       # get app dir from config
    pdvd_setup = utils.ReadConfig(app_name, "setup")                            # get app setup exe from config
    media_path = utils.ReadConfig("media", media_type)
    if (media_path is not None) and (media_path != "") and (media_path != "NC")\
       and ('FAIL:' not in media_path):
        library.write_log(lib_constants.LOG_INFO, "INFO: Playback media found"
        " %s"%media_path, test_case_id, script_id, "None", "None", log_level,
        tbd)                                                                    #writing log info message to the log file
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Playback media "
        "file not updated in config.ini", test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing log warning message to the log file
        return False
    if ('FAIL' in pdvd_tool_dir) or ('FAIL' in pdvd_setup):
        library.write_log(lib_constants.LOG_WARNING, "WARNING: PDVD tool "
        "location not found in config.ini", test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing log warning message to the log file
        return False
    pdvd_exe = os.path.join(pdvd_tool_dir, pdvd_setup)
    cmd_pdvd = "\""+str(pdvd_exe)+"\""+" "+"\""+media_path+"\""
    _thread.start_new_thread(play_media_wmp, (cmd_pdvd,))                        #start thread for playback using application
    time.sleep(lib_constants.TEN_SECONDS)
    status = find_app_window_wmp("PowerDVD", test_case_id, script_id,
                                 log_level, tbd)
    return status

###############################################################################
# Function Name : play_file_vlc
# Parameters    : media_type,test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To launch and verify this is the main function
###############################################################################
def play_file_vlc(media_type, test_case_id, script_id, log_level="All",
                  tbd=None):
    app_name = "vlc"
    vlc_tool_dir = utils.ReadConfig(app_name, "tooldir")                       # get app dir from config
    vlc_setup = utils.ReadConfig(app_name, "setup")                            # get app setup exe from config
    if ('FAIL' in vlc_tool_dir) or ('FAIL' in vlc_setup):
        library.write_log(lib_constants.LOG_WARNING, "WARNING: VLC tool "
        "location not found in config.ini", test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing log warning message to the log file
        return False
    media_path = utils.ReadConfig("media", media_type)
    if (media_path is not None) and (media_path != "") and (media_path != "NC")\
        and ('FAIL:' not in media_path):
        library.write_log(lib_constants.LOG_INFO, "INFO: Playback media found"
        " %s"%media_path, test_case_id, script_id, "None", "None", log_level,
        tbd)                                                                    #writing log info message to the log file
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Playback media "
        "file not updated in config.ini", test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing log warning message to the log file
        return False
    vlc_exe = os.path.join(vlc_tool_dir, vlc_setup)
    cmd_vlc = "\""+str(vlc_exe)+"\""+" "+"\""+media_path+"\""
    _thread.start_new_thread(play_media_wmp, (cmd_vlc,))                         #start thread for playback using application
    time.sleep(lib_constants.TEN_SECONDS)
    dir, file_name = os.path.split(media_path)
    window_name = file_name+" - "+"VLC media player"
    status = find_app_window_wmp(window_name, test_case_id, script_id,
                                 log_level, tbd)
    return status
###############################################################################
# Function Name : play_file_using_player
# Parameters    : media_type,test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To launch and verify this is the main function
###############################################################################
def play_file_using_player(token, test_case_id, script_id, log_level="All",
                           tbd=None):                                           #function to check playback and error
    match = re.search(r".*lay.(\w+).*?using.*?(\w+)", token,re.I)               #re for getting file and application
    media_type, app_name = list(map(str, match.groups()))
    if 'wmp' in app_name:
        status = play_file_windows_media_player(media_type, test_case_id,
                                                    script_id, log_level, tbd)
        return status
    elif 'pdvd' in app_name:
        status = play_file_pdvd(media_type, test_case_id, script_id, log_level,
                                    tbd)
        return status
    elif 'vlc' in app_name:
        status = play_file_vlc(media_type, test_case_id, script_id, log_level,
                                   tbd)
        return status
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Application type"
        " is not supported %s"%app_name, test_case_id, script_id, log_level,
        tbd)                                                                    #Writing log warning essage to the log file
        return False

###############################################################################
# Function Name : play_file_windows_media_player
# Parameters    : media_type,test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To launch and verify this is the main function
###############################################################################
def play_file_windows_media_player(media_type, test_case_id, script_id,
                                   log_level="All", tbd=None):                  # main function to check playback and error

    app_name = "WMPLAYER"
    wmp_tool_dir = utils.ReadConfig(app_name, "tooldir")                        #extracting wmp tool dir from config file
    wmp_setup = utils.ReadConfig(app_name, "setup")                             #extracting wmp setup from config file
    media_path = utils.ReadConfig("MEDIA", media_type)                          #extracting media type from config file
    if media_type.lower() in lib_constants.AUDIO_FORMAT:
        media_type = "audio"
    elif media_type.lower() in lib_constants.VIDEO_FORMAT:
        media_type = "video"
    elif "av" == media_type.lower():
        media_type = "video"
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Media type is "
        "not supported %s"%media_type, test_case_id, script_id, log_level, tbd) #Writing log warning message to the log file
        return False

    if "FAIL:" in [media_path, wmp_tool_dir, wmp_setup]:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
        "the config entry for media_path, wmp_tooldir, wmp_setup", test_case_id,
        script_id, "None", "None", log_level, tbd)                              #Writing log warning message to the log file
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Config entry found ",
        test_case_id, script_id, "None", "None", log_level, tbd)                #writing log info message to the log file

    if os.path.exists(media_path):
        library.write_log(lib_constants.LOG_INFO, "INFO: %s file exists in "
        "given media_path"%media_type, test_case_id, script_id, "None", "None",
        log_level, tbd)                                                         #writing log info message to the log file
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to get "
        "%s file from given media_path as %s"%(media_type, media_path),
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing log warning message to the log file
        return False
    status = create_wmp_regedit(test_case_id, script_id, log_level, tbd)
    if status:
        pass
    else:
        return False

    wmp_exe = os.path.join(wmp_tool_dir, wmp_setup)
    cmd_wmp = "\""+str(wmp_exe)+"\""+" "+"\""+media_path+"\" /fullscreen"
    _thread.start_new_thread(play_media_wmp, (cmd_wmp,))                         # start thread for playback using application
    time.sleep(lib_constants.FIVE_SECONDS)
    playback_status = verify_playback(test_case_id, script_id, log_level, tbd)  # verify playback call
    if playback_status:
        library.write_log(lib_constants.LOG_INFO, "INFO: Playback has been "
        "initiated", test_case_id, script_id, "None", "None", log_level, tbd)   #writing log info message to the log file
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Playback "
        "initiation failed", test_case_id, script_id, "None", "None", log_level,
        tbd)                                                                    #Writing log warning message to the log file
        return False

###############################################################################
# Function Name : compare_image
# Parameters    : percentage,media_type,test_case_id,script_id,log_level,tbd
# Return Value  : return true / false
# Purpose       : To launch and verify this is the main function
###############################################################################


def compare_image(percentage, media_type, test_case_id, script_id,
                  log_level="All", tbd=None):

    if "audio" == media_type:
        if percentage >= lib_constants.AUDIO_PASS_PERCENTAGE:                   # check for audio verification
            library.write_log(lib_constants.LOG_INFO, "INFO: Audio image "
            "compare passed", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #writing log info message to the log file
            return True

    elif "video" == media_type:                                                 # check for video verification
        if percentage <= lib_constants.VIDEO_PASS_PERCENTAGE:
            library.write_log(lib_constants.LOG_INFO, "INFO : Video image "
            "compare passed", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #writing log info message to the log file
            return True

    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Playback image "
        "compare Failed", test_case_id, script_id, "None", "None", log_level,
        tbd)                                                                    #writing log info message to the log file
        return False

###############################################################################
# Function Name : create_wmp_action
# Parameters    : action,tc_id,script_id,loglevel="ALL",tbd=None
# Return Value  : true / false
# Purpose       : To check error in playback and verify playback
# Volume Down: F8
# Volume Up: F9
# Play/Pause: Ctrl + Alt + Home
# Fast forwards playing content: Ctrl + Shift + F
# Rewinds playing content: Ctrl + Shift + B
# Next (Item or Chapter): Ctrl + F
# Previous (Item or Chapter): Ctrl + B
# Full Screen Toggle: Alt + Enter
###############################################################################

def create_wmp_action(action, test_case_id, script_id, log_level="ALL",
                          tbd=None):
    try:
        if "play" == action.lower() or "pause" == action.lower():               #play/pause action
            pyautogui.hotkey('ctrl', 'p')
            pyautogui.press('f8')
        elif "vol_up" == action.lower():                                        # volume up action
            pyautogui.press('volumeup')
            pyautogui.press('f9')
        elif "vol_down" == action.lower():                                      # volume down action
            pyautogui.press('volumedown')
        elif "mute" == action.lower() or "unmute" == action.lower():            # mute /unmute action
            pyautogui.press('volumemute')
        elif "stop" == action.lower():                                          # stop action
            pyautogui.hotkey('ctrl', 'w')
        elif "fwd" == action.lower():                                           # forward action
            pyautogui.hotkey('ctrl', 'Shift', 'F')
        elif "rewind" == action.lower():                                        # rewind action
            pyautogui.hotkey('ctrl', 'Shift', 'B')
        elif "next" == action.lower():
            pyautogui.hotkey('ctrl', 'F')
        elif "previous" == action.lower():
            pyautogui.hotkey('ctrl', 'B')
        elif "toggle window" == action.lower():
            pyautogui.hotkey('Alt', 'Enter')
        library.write_log(lib_constants.LOG_INFO, "INFO: Playback action "
        "performed %s"%action, test_case_id, script_id, None, None, log_level,
        tbd)                                                                    #writing log info message to the log file
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "executing playback action %s"%e, test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #writing log info message to the log file
        return False
__author__ = 'NARESHGX'
############################General Python Imports##############################
from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import subprocess
import re
from win32api import GetSystemMetrics
import win32api
import os
import time
import pyaudio
import struct
import math
import glob
import codecs
from desktopmagic.screengrab_win32 import (getDisplayRects,getDisplaysAsImages)
############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_play_filetype_using_application
import lib_plug_unplug
################################################################################
# Global Constants for local use
################################################################################
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = lib_constants.SHORT_NORMALIZE
CHANNELS = lib_constants.CHANNELS
RATE = lib_constants.RATE
INPUT_BLOCK_TIME = lib_constants.INPUT_BLOCK_TIME
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
audiodevin = ""
quality_flag = ""
raritan_flag = False
hdmi_display_flag = False
################################################################################
# Function Name : select_audio_device
# Parameters    : None
# Return Value  : Input device i.e. mic
# Purpose       : to get input device list and primary
################################################################################
def select_audio_device(tc_id,script_id,log_level,tbd):                         # Select an audio device from device list
    global audiodevin
    pa = pyaudio.PyAudio()
    try:
        ndev = pa.get_device_count()
        n_list = 0
        while n_list < ndev:                                                    # from device list check for required jack connection
            s = pa.get_device_info_by_index(n_list)
            if s['maxInputChannels'] > 0 and 'External Mic' in s['name']:
                audiodevin = int(s['index'])
            n_list = n_list + 1
        pa.terminate()
        if isinstance(audiodevin, int):                                         # if required jack is found then return index value of device
            library.write_log(lib_constants.LOG_INFO,"INFO: External MIC index"
                    " is %s"%audiodevin,tc_id,script_id,None,None,log_level,tbd)
            return audiodevin
        else:                                                                   # else return none
            return None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: No audio device "
                        "list found",tc_id,script_id,None,None,log_level,tbd)
        return None
################################################################################
# Function Name : get_rms
# Parameters    : block
# Return Value  : amplitude
# Purpose       : get amplitude of a given block of sample
################################################################################
def get_rms(block):                                                             # get amplitude function
    count = len(block)/2                                                        # RMS amplitude is defined as the square root of the
    format = "%dh"%(count)                                                      # mean over time of the square of the amplitude.
    shorts = struct.unpack( format, block )                                     # so we need to convert this string of bytes into a string of 16-bit samples...
    sum_squares = 0.0                                                           # we will get one short out for each  two chars in the string. iterate over the block.
    for sample in shorts:                                                       # sample is a signed short in +/- 32768.
        n = sample * SHORT_NORMALIZE                                            #  normalize it to 1.0
        sum_squares += n*n
    return math.sqrt( sum_squares / count )

################################################################################
# Function Name : verify_media_playback
# Parameters    : token,tc_id,script_id,log_level,tbd
# Return Value  : playback status true/false
# Purpose       : to call function depending upon playback type audio/video
################################################################################
def verify_media_playback(token,tc_id,script_id,log_level="All",tbd=None):
    global quality_flag
    re_fetch = re.findall('.*verify (.*?) playback on (.*)',
                          token,re.I)[0]                                        # re for fetching media type
    params = (re_fetch[0]).strip()
    if "audio" in params.lower() and "quality" in params.lower() and "online" \
            in params.lower():
        media_type = "audio"
        quality_flag = True
        online_flag = True
    elif ("video" in params.lower() or "av" in params) and "quality" in \
            params.lower() and "online" in params.lower():
        media_type = "video"
        quality_flag = True
        online_flag = True
    elif "audio" in params and "quality" in params:
        media_type = "audio"
        quality_flag = True
    elif ("video" in params or "av" in params) and "quality" in params:
        media_type = "video"
        quality_flag = True
    elif "video" in params or "auido" in params:
        media_type = params.strip()
        quality_flag = False
    else:
        media_type = params.strip()
        quality_flag = False
    device_type = (re_fetch[1]).strip()
    cmd_to_check_wmp = 'tasklist'                                               #command to check if that application stared or not
    cmd_out = subprocess.Popen(cmd_to_check_wmp, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE)     # check for wmplayer process id if found continue
    if 'wmplayer' in cmd_out.communicate()[0]:
        library.write_log(lib_constants.LOG_INFO,"INFO: WMPlayer application is"
                        " alive", tc_id, script_id, None, None, log_level, tbd)
    else:                                                                       # else re-launch and continue
        status = lib_play_filetype_using_application.\
           play_file_windows_media_player(media_type, tc_id, script_id,
                                         log_level, tbd)
        if status:                                                              # check launch status if lunched successfully continue
            library.write_log(lib_constants.LOG_INFO,"INFO: WMPlayer "
            "application not found re-launched ", tc_id, script_id, None,None,
                              log_level, tbd)
        else:                                                                   # check launch status if lunched unsuccessfully return false
            library.write_log(lib_constants.LOG_INFO,"INFO: Re-launching "
            "WMPlayer failed", tc_id, script_id, None,None,log_level, tbd)
            return False, 'AUDIO/VIDEO'
    media_path = utils.ReadConfig("media", media_type)
    if (media_path is not None) and (media_path != "") and (media_path != "NC")\
            and ('FAIL:' not in media_path):
        library.write_log(lib_constants.LOG_INFO, "INFO : Playback media "
                                                  "found %s" % (media_path),
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO : Playback media "
                                                  "file not updated in "
                                                  "config.ini", tc_id,
                          script_id, "None", "None", log_level, tbd)
        return False
    if "AUDIO" == media_type.upper():                                           # audio function call
        status = verify_audio_on_jack(tc_id,script_id,log_level,tbd)
        return status, 'Audio'
    elif "VIDEO" == media_type.upper():                                         # video function call
        status = verify_video_on_display(device_type, quality_flag, media_path,
                                         tc_id, script_id, log_level, tbd)
        return status, 'Video'
    elif "AV" == media_type.upper():
        status_video = verify_video_on_display(device_type, quality_flag,
                                               media_path, tc_id, script_id,
                                               log_level, tbd)
        status_audio = verify_audio_on_jack(tc_id, script_id, log_level, tbd)
        if True == status_audio and True == status_video:
            library.write_log(lib_constants.LOG_INFO,"INFO: Audio video "
            "playback verification is successful", tc_id, script_id, None,
                              None, log_level, tbd)
            return True, 'AV'
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO: Media type not "
                            "supported",tc_id,script_id,None,None,log_level,tbd)
        return False, 'Audio/Video'
################################################################################
# Function Name : verify_audio_on_jack
# Parameters    : tc_id,script_id,log_level,tbd
# Return Value  : return true or false
# Purpose       : verify audio playback on 3.5mm jack
################################################################################
def verify_audio_on_jack(tc_id,script_id,log_level="All",tbd=None):
    count = countf = countn = countvol = 0
    log_data = ""
    log_data_arr = []
    log_path = script_id.replace(".py", ".log")
    log_path = os.path.join(lib_constants.SCRIPTDIR,log_path)
    device_index = select_audio_device(tc_id,script_id,log_level,tbd)
    if isinstance(device_index,int):                                            # check for audio jack connection to mic
        library.write_log(lib_constants.LOG_INFO,"INFO: Audio jack 3.5mm is "
                        "Connected",tc_id,script_id,None,None,log_level,tbd)
    else:                                                                       # if no connection found return false
        library.write_log(lib_constants.LOG_INFO,"INFO: Connection from "
    "audio out to mic in not present",tc_id,script_id,None,None,log_level,tbd)
        return False
    try:
        if os.path.exists(log_path):
            os.remove(log_path)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in deleting "
        "old log file",tc_id,script_id,None,None,log_level,tbd)
        return False
    log_file = open(log_path,'w')
    pa = pyaudio.PyAudio()
    try:
        stream = pa.open(format = FORMAT, channels=CHANNELS, rate = RATE,
                     input = True, frames_per_buffer = INPUT_FRAMES_PER_BLOCK,
                     input_device_index = device_index)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in getting "
                                                  "stream", tc_id, script_id,
                          None, None, log_level, tbd)
        return False
    for i in range(lib_constants.THOUSAND):
        try:
            block = stream.read(INPUT_FRAMES_PER_BLOCK)                         # read frames per block
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Connection from "
    "audio out to mic in not present or nothing is being heard on sensor %s"%e,
                              tc_id, script_id, None, None, log_level, tbd)
            return False
        try:
            amplitude = get_rms(block)
            log_data = log_data + str(amplitude)+'\n'                           # add to log
            log_data_arr.append(str(amplitude))
            if "-05" in str(amplitude):                                         # if value is -05 then no connection is made and nothing is being heard
                countf = countf+1
                if countf > lib_constants.WAIT_TIME:                            # check for 30 times if connection is proper
                    library.write_log(lib_constants.LOG_INFO,"INFO: Connection "
                    "from audio out to mic in not present or nothing is "
                    "being heard on sensor",tc_id, script_id, None,
                                      None, log_level, tbd)
                    log_file.write(log_data)
                    log_file.close()
                    return False
            elif amplitude > lib_constants.POINT_ONE_SECONDS:                   # if its to loud...
                count = count+1
                if count > lib_constants.FIVE_HUNDRED:                          # check for 500 times for amplitude to verify audio is proper
                    library.write_log(lib_constants.LOG_INFO,"INFO: Audio "
                    "verification is Proper on 3.5mm jack",tc_id,script_id,None,
                                      None,log_level,tbd)
                    log_file.write(log_data)
                    log_file.close()
                    plt.xlabel('Times')
                    plt.ylabel('Amplitude')
                    plt.plot(log_data_arr)
                    plt.savefig(script_id.replace('.py', '.png'),
                                dpi=lib_constants.FIVE_HUNDRED)
                    return True
            elif amplitude < lib_constants.POINT_ZERO_ONE_SECONDS:
                countn = countn+1
                if countvol > lib_constants.THREE:                              # check for count if after increasing vol amplitude is not increasing return false
                    library.write_log(lib_constants.LOG_INFO,"INFO: Audio is "
                "still having noise Audio verification Failed",tc_id,script_id,
                                      None,None,log_level,tbd)
                    log_file.write(log_data)
                    log_file.close()
                    return False
                if countn > lib_constants.TEN:                                  # if no. of count for amplitude less than 1 increase volume
                    library.write_log(lib_constants.LOG_INFO,"INFO: Audio level"
                " is below sensor level increasing volume",tc_id,script_id,None,
                                      None,log_level,tbd)
                    lib_play_filetype_using_application.create_wmp_action\
                        ("vol_up",tc_id, script_id, None, None, log_level, tbd) # increase volume using lib
                    countvol = countvol+1
                    countn = 0
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception found "
                                "%s"%e,tc_id,script_id,None,None,log_level,tbd)
            return False

################################################################################
# Function Name : split_video_frames
# Parameters    : video_path
# Return Value  : none
# Purpose       : to split video to frames
################################################################################
def split_video_frames(video_path, tc_id, script_id, log_level, tbd):
    x = GetSystemMetrics(0)
    y = GetSystemMetrics(1)
    ffmpeg_path = utils.ReadConfig("media","ffmpeg_path")
    if "fail" not in ffmpeg_path and os.path.exists(ffmpeg_path):
        library.write_log(lib_constants.LOG_INFO,"INFO: FFMPEG path "
            "found", tc_id, script_id, None, None, log_level ,tbd)
        if not os.path.exists("frames"):
            try:
                os.makedirs("frames")
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
                                                      "creating capture folder",
                              tc_id,script_id,None,None,log_level,tbd)
                return False
            cmd_ffmpeg = ffmpeg_path+" -i "+ video_path +" -s "+ str(x) +"x"+ \
                str(y) +" -ss 00:00:00 -to 00:00:30 frames\\ffmpeg_%0d.png"
            proc = subprocess.Popen(cmd_ffmpeg, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE)
            exec_out = proc.communicate()[0]
            if "fail" not in exec_out:
                library.write_log(lib_constants.LOG_INFO,"INFO: Video frames"
                " extracted into frames directory successfully", tc_id,
                                  script_id, None, None, log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Video frames"
                " extraction failed", tc_id, script_id, None, None, log_level,
                                  tbd)
                return False
        else:
            cmd_ffmpeg = ffmpeg_path+" -i "+ video_path +" -s "+ str(x) +"x"+ \
                str(y) +" -ss 00:00:00 -to 00:00:30 frames\\ffmpeg_%0d.png"
            proc = subprocess.Popen(cmd_ffmpeg, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE)
            exec_out = proc.communicate()[0]
            if "fail" not in exec_out:
                library.write_log(lib_constants.LOG_INFO,"INFO: Video frames"
                " extracted into frames directory successfully", tc_id,
                                  script_id, None,
                                  None, log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Video frames"
                " extraction failed", tc_id, script_id, None, None, log_level,
                                  tbd)
                return False
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO: FFMPEG file not found "
        "in tools directory ", tc_id, script_id, None, None, log_level, tbd)
        return False

################################################################################
# Function Name : mse
# Parameters    : imageA, imageB
# Return Value  : return the MSE, the lower the error, the more "similar"
# Purpose       : the 'Mean Squared Error' between the two images is the
# sum of the squared difference between the two images;
# NOTE: the two images must have the same dimension
################################################################################
def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

################################################################################
# Function Name : frames_compare
# Parameters    : imageA, imageB
# Return Value  : return true or false
# Purpose       : verify video playback on device
################################################################################

def frames_compare(imageA, imageB, j, tc_id, script_id, log_level, tbd):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    s = ssim(imageA, imageB)
    # setup the figure
    fig = plt.figure("Captured Frame vs Original Frame")
    os.chdir(lib_constants.SCRIPTDIR)
    if int(m) < lib_constants.VIDEO_PASS_SSIM and float(s*100) > \
            lib_constants.VIDEO_PASS_PERCENTAGE:
        plt.suptitle("MSE: %.2f, SSIM: %.2f, Result: Pass\n "
                     "Captured Frame vs Original Frame" % (m, s))
        # show first image
        ax = fig.add_subplot(1, 2, 1)
        plt.imshow(imageA, cmap = plt.cm.gray)
        plt.axis("off")
        # show the second image
        ax = fig.add_subplot(1, 2, 2)
        plt.imshow(imageB, cmap = plt.cm.gray)
        plt.axis("off")
        # show the images
        plt.savefig(script_id.replace(".py", "-"+str(j)+".png"),
                    dpi=lib_constants.FIVE_HUNDRED)
        return True,m,s
    else:
        plt.suptitle("MSE: %.2f, SSIM: %.2f, Result: Fail" % (m, s))
        return False,m,s

################################################################################
# Function Name : win32_set_res
# Parameters    : width=None, height=None, depth=32, tc_id, script_id,
#                 log_level, tbd
# Return Value  : return true or false
# Purpose       : Set the primary windows display to the specified mode
# Gave up on ctypes, the struct is really complicated
# user32.ChangeDisplaySettingsW(None, 0)
################################################################################
def win32_set_res(tc_id, script_id, log_level, tbd, width=None, height=None,
                  depth=32):
    try:
        if width and height:
            if not depth:
                depth = 32
            mode = win32api.EnumDisplaySettings()
            mode.PelsWidth = width
            mode.PelsHeight = height
            mode.BitsPerPel = depth
            win32api.ChangeDisplaySettings(mode, 0)
            return True
        else:
            win32api.ChangeDisplaySettings(None, 0)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
                                                      "creating capture folder",
                              tc_id,script_id,None,None,log_level,tbd)
        return False

################################################################################
# Function Name : verify_video_on_display
# Parameters    : tc_id,script_id,log_level,tbd
# Return Value  : return true or false
# Purpose       : verify video playback on device
################################################################################
def verify_video_on_display(device_type, quality, media_path, tc_id, script_id,
                            log_level="All", tbd=None):
    try:
        global raritan_flag
        global hdmi_display_flag
        status, device_name = lib_plug_unplug.display_type_verify("EDP",
                                            tc_id, script_id, log_level, tbd)
        if status:
            library.write_log(lib_constants.LOG_INFO,"INFO: Display panel "
            "found for video verification", tc_id, script_id, None, None,
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Display panel "
            "not found for video verification", tc_id, script_id, None, None,
                              log_level, tbd)
            return False
        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")                       #Read the tools directory path from the config and store in tool_dir
        cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")
        if "FAIL:" in [tool_dir, cmd_to_run]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING:config values"
            "under DISPLAY section are missing", tc_id, script_id,
            "None", "None",log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:config values "
            "under DISPLAY section are found", tc_id, script_id, "None",
            "None",log_level, tbd)
            utils.filechangedir(tool_dir)
            cmd_exe = subprocess.Popen(cmd_to_run, shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE)#Execute the command to get the display property
            if "" != cmd_exe.communicate()[0]:                                  #Failed to execute the command
                return False                                                    #return "False", None
            else:
                file = glob.glob("DisplayInfo.txt")                             #check for displayinfo.txt in the directory
                if [] == file:                                                  #if file is empty
                    return False                                                #return "false", None
                else:
                    utils.filechangedir(tool_dir)                               #change to tools directory where tool is kept
                    with codecs.open("DisplayInfo.txt","r", "utf-8") as handle: #file operation open file in utf-8 mode and save the texts in handle
                        for line in handle:                                     #iterate through the lines
                            if "Raritan" in line:
                                raritan_flag = True
                            if "HDMI" in line and raritan_flag != True:
                                hdmi_display_flag = True

        if raritan_flag:
            status = win32_set_res(tc_id, script_id, log_level, tbd,
                                   width=1280, height=720)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                                "to 1280x720 for capturing frames",
                                  tc_id, script_id, None, None, log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                "failed to capture frames", tc_id, script_id, None, None,
                                  log_level, tbd)
                return False
        elif hdmi_display_flag:
            status = win32_set_res(tc_id, script_id, log_level, tbd,
                                   width=1280, height=720)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                                "to 1280x720 for capturing frames",
                                  tc_id, script_id, None, None, log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                "failed to capture frames", tc_id, script_id, None, None,
                                  log_level, tbd)
                return False
        else:
            status = win32_set_res(tc_id, script_id, log_level, tbd,
                                   width=1600, height=900)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                                "to 1600x900 for capturing frames",
                                  tc_id, script_id, None, None, log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Resolution set "
                "failed to capture frames", tc_id, script_id, None, None,
                                  log_level, tbd)
                return False
        os.chdir(lib_constants.SCRIPTDIR)
        win32api.SetCursorPos((lib_constants.CURSOR_POS_DEFAULT, lib_constants.
                                   CURSOR_POS_DEFAULT))
        time.sleep(lib_constants.TEN)
        if not os.path.exists("capture"):
            try:
                os.makedirs("capture")
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
                                                      "creating capture folder",
                              tc_id,script_id,None,None,log_level,tbd)
                return False
        if "edp" in device_type.lower():
            displayNumber = 1
            device_type = 1
        for i in range(lib_constants.FIVE):
            c_name = "capture\\capture%s.png"%(i+1)
            for displayNumber, im in enumerate(getDisplaysAsImages(),1):
                if device_type == displayNumber:
                    im.save(c_name,format='png')
        library.write_log(lib_constants.LOG_INFO, "INFO : Capture playback "
            "frames",tc_id, script_id, "None", "None", log_level,
                              tbd)
        if (media_path is not None) and (media_path != "") and \
                (media_path != "NC") and ('FAIL:' not in media_path):
            library.write_log(lib_constants.LOG_INFO, "INFO : Playback media "
                                                      "found %s" % (media_path),
                              tc_id, script_id, "None", "None", log_level,
                              tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Playback media "
                                                      "file not updated in "
                                                      "config.ini", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        status = split_video_frames(media_path, tc_id, script_id, log_level,
                                    tbd)
        if status:
            org_file = len(os.walk('frames').next()[2])
            capt_file = len(os.walk('capture').next()[2])
            k = 1
            flag_count = 0
            try:
                for j in range(1, capt_file):
                    for i in range(k, org_file):
                                                                                    # load the images -- the original & contrast frames
                        original = cv2.imread("capture//capture%s.png"%j)
                        contrast = cv2.imread('frames//ffmpeg_%s.png'%i)
                                                                                    # convert the images to grayscale
                        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
                        contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
                        status, m, s = frames_compare(original, contrast, j,
                                            tc_id, script_id, log_level, tbd)
                        if status:
                            k = i
                            flag_count = flag_count + 1
                            break
                        elif flag_count >= lib_constants.ONE and \
                                        quality != True:
                            library.write_log(lib_constants.LOG_INFO,"INFO: "
                                "Video playback on display is verified", tc_id,
                                          script_id, None, None, log_level,tbd)
                            return True
                        elif 0 == flag_count and \
                                        j > lib_constants.ONE and \
                                        quality != True:
                            library.write_log(lib_constants.LOG_INFO,"INFO: "
                                "Fail to verify Video playback capture frame",
                                tc_id, script_id, None, None, log_level,tbd)
                            return False
                        elif j == lib_constants.FIVE and flag_count == 5:
                            break
                        else:
                            pass
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,"ERROR: "
                "Exception in video playback verification %s"%e, tc_id,
                                  script_id, None, None, log_level,tbd)
                return False
            if flag_count == lib_constants.FIVE and True == quality :
                library.write_log(lib_constants.LOG_INFO,"INFO: "
            "Video quality playback on display is verified and satisfies the "
            "quality condition", tc_id, script_id, None, None, log_level,tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: "
                "Video validation unsuccessful",tc_id, script_id, None, None,
                                  log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception found due "
                                        "to %s"%e, tc_id, script_id,
                                          None, None, log_level, tbd)
        return False
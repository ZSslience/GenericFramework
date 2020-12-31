__author__ = 'NARESHGX'
############################General Python Imports##############################
import re
import os.path
import wave
import pyaudio
############################Local Python Imports################################
import lib_play_filetype_using_application
import library
import lib_constants
######################global constants to be used locally#######################
CHUNK = lib_constants.ONE_KB
FORMAT = pyaudio.paInt16
CHANNELS = lib_constants.CHANNELS
RATE = lib_constants.RATE
audiodevin = ""
pa = pyaudio.PyAudio()
################################################################################
################################################################################
#   Function name   : video_playback_control
#   description     : To perform windows media player different actions
#   parameters      : 'testcase_id' is test case id
#                     'script_id' is script id
#                     'ostr ' is original string
#   Returns         : True/False
######################### Main script ##########################################
def video_playback_control(ostr,testcase_id,script_id,log_level="ALL",tbd=None):
    match = re.search(r'.*?Select.(\w+).(\w+).in(.\w+)(.* for( [0-9]+))?.*',
                                                                     ostr ,re.I)# re for fetching mediatype ,app_player,action and seconds
    action, media_type, app_player, optn1, seconds = list(map(str, match.groups()))
    media_type = media_type.strip()
    app_player = app_player.strip()
    action = action.strip()
    try:
        if "WMP" in app_player.upper():                                         # windows media player commands
            if lib_play_filetype_using_application.verify_playback(testcase_id,
                                                    script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,"INFO: WMPlayer "
                "application is active",testcase_id, script_id, None, None,
                                  log_level,tbd)
                if lib_play_filetype_using_application.create_wmp_action(
                    action.lower(), testcase_id, script_id, log_level, tbd):    # if windows media player found perform action log is printed by lib
                    return True,'PASS'
                else:
                    return False,'FAIL'
            else:
                if lib_play_filetype_using_application\
                        .play_file_windows_media_player(media_type, testcase_id,
                                                    script_id, log_level, tbd): #if windows media player not found launch
                    library.write_log(lib_constants.LOG_INFO,"INFO: Launching "
        "WMPlayer application for 1st time", testcase_id, script_id, None, None,
                                      log_level,tbd)
                    if lib_play_filetype_using_application.create_wmp_action\
                        (action.lower(), testcase_id, script_id, log_level, tbd):
                        return True, 'PASS'
                    else:
                        return False, 'FAIL'
                else:
                    return False, 'FAIL'
        elif ("RECORD" in action.upper()) or ("STOP" in action.upper()):        # block for record test case
            if ("SOUND" in app_player.upper()) and ("RECORD" in action.upper()):
                seconds = int(seconds.strip())
                RECORD_SECONDS = seconds
                status,file_path = record_clip_save_file(RECORD_SECONDS,
                                       testcase_id, script_id, log_level, tbd)  # call function to save recorded file
                if (True == status) and os.path.isfile(file_path):
                    library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Recorded "
                    "file is found and valid", testcase_id, script_id, None,
                                                    file_path, log_level, tbd)
                    return True, file_path
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Recorded "
                "file is not found ", testcase_id, script_id, None, file_path,
                                      log_level, tbd)
                    return False, 'FAIL'
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "performing playback controls %s"%e, testcase_id, script_id, None,
                          None, log_level, tbd)
        return False, 'FAIL'
################################################################################
#   Function name   : select_audio_device
#   description     : To select audio port to mic port
#   parameters      : 'tc_id' is test case id
#                     'script_id' is script id
#   Returns         : device index
######################### Main script ##########################################
def select_audio_device(tc_id,script_id,log_level,tbd):                         # Select an audio device from device list
    global audiodevin
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
            library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Audio device "
        "index is found at % index"%audiodevin, tc_id, script_id, None, None,
                          log_level,tbd)
            return audiodevin
        else:                                                                   # else return none
            library.write_log(lib_constants.LOG_DEBUG,"DEBUG: No audio device "
                                    "list found", tc_id, script_id, None, None,
                          log_level, tbd)
            return None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: No audio device "
                "list found", tc_id, script_id, None, None,log_level, tbd)
        return None
################################################################################
#   Function name   : record_clip_save_file
#   description     : to record and save the clip
#   parameters      : 'RECORD_SECONDS,tc_id,script_id,log_level="ALL",tbd=None
#   Returns         : device index
######################### Main script ##########################################
def record_clip_save_file(RECORD_SECONDS, tc_id, script_id, log_level="ALL",
                          tbd=None):
    WAVE_OUTPUT_FILENAME = script_id.replace('.py', '.wav')
    device_index = select_audio_device(tc_id, script_id, log_level, tbd)
    if isinstance(device_index,int):                                            # check for audio jack connection to mic
        library.write_log(lib_constants.LOG_INFO,"INFO: MIC jack 3.5mm is "
                                "Connected", tc_id, script_id, None, None,
                          log_level, tbd)
    else:                                                                       # return false if no connection found
        library.write_log(lib_constants.LOG_INFO,"INFO Connection from "
        "audio out to mic in not present", tc_id, script_id, None, None,
                          log_level, tbd)
        return False,'FAIL'
    try:
        p = pyaudio.PyAudio()                                                   # get pyaudio object
        stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index = device_index)                          # set properties for pyaudio
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):                  # add stream to frames
            data = stream.read(CHUNK)
            frames.append(data)                                                 # 2 bytes(16 bits) per channel

        stream.stop_stream()                                                    # stop stream
        stream.close()                                                          # close stream
        p.terminate()                                                           # close terminate
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')                              # save file
        wf.setnchannels(CHANNELS)                                               # save file with below properties
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        file_path = os.path.abspath(WAVE_OUTPUT_FILENAME)
        library.write_log(lib_constants.LOG_INFO,"INFO: Recorded file path is "
                    "%s"%file_path,tc_id, script_id, None, None, log_level, tbd)
        return True,file_path
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR connection from "
        "audio out to mic in not present", tc_id, script_id, None, None,
                          log_level, tbd)
        return False,'FAIL'
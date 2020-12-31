__author__ = "sivakisx"

##############################General Library import############################
import os
import utils
import time
import sys
import subprocess
#########################Local library import###################################
import lib_constants
import library
################################################################################
# Function Name : open_image_file
# Parameters    : token,test_case_id , script_id , tbd ,log_level
#  Functionality : open image or file(mp3 or mp4)
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################
def open_image_file(token,test_case_id, script_id, log_level="ALL",
                     tbd="None"):
    token_list = token.split(' ')
    image_format = lib_constants.IMAGE_FORMAT_TYPE
    file_format = lib_constants.FILE_FORMAT_TYPE
    dir_path = utils.ReadConfig("IMAGE_FILE_PATH","OBJECT_PATH")
    if "FAIL:" in dir_path:
        library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "get object path from Config.ini under tag [IMAGE_FILE_PATH] "
            ,test_case_id, script_id,"None", "None", log_level, tbd)            # Failed to get info from config file
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Dir_path for "
            "image_file_path is identified as %s from config.ini" %dir_path,
            test_case_id,script_id, "None", "None", log_level, tbd)             # Path information obtained..continue

    if "USING" in token_list:
        file_type, pos = utils.extract_parameter_from_token(token_list, "OPEN",
                                                        "USING", log_level, tbd)#Extract the file_type from the token
        exe_file,pos= utils.extract_parameter_from_token(token_list,
                                            "USING", "",log_level, tbd)         #Extract the exe_file from the token
        exe_name = utils.ReadConfig("IMAGE_FILE_PATH", exe_file)
        try:
            if os.path.isfile(dir_path):
                if [file for file in image_format if dir_path.endswith(file)] \
                or [file for file in file_format if dir_path.endswith(file)]:   #checking given input is image or file
                    subprocess.check_output("%s %s" %(exe_name,dir_path))
                    library.write_log(lib_constants.LOG_INFO,"INFO: Image "
                        " opened successfully", test_case_id,script_id,
                        "None", "None", log_level, tbd)                         #if file is opened genarate pass log
                    return True
                elif [file for file in image_format if file_type.endswith(file)]\
                or [file for file in file_format if file_type.endswith(file)]:
                    [path for path in os.walk(r'C:\\') if file_type in path ]   #searching for file in c Drive:
                    subprocess.Popen("%s %s" %(exe_name,file_type))
                    library.write_log(lib_constants.LOG_INFO,"INFO: Image "
                        "/File opened successfully", test_case_id,script_id,
                            "None", "None", log_level, tbd)                     #if file is opened genarate pass log
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Input "
                        "image\filepath is incorrect",test_case_id, script_id,
                        "None", "None",log_level, tbd)                          # write error message to log
                    return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
            test_case_id, script_id, "None", "None", log_level, tbd)            #exception error catch if failed
            return False
    else:
        file_type, pos = utils.extract_parameter_from_token(token_list, "OPEN",
                                                        "", log_level, tbd)     #Extract the image/file type from the token
        exe_file = None
        exe_name = None
        try:
            if os.path.isfile(dir_path):
                if [file for file in image_format if dir_path.endswith(file)] or \
                [file for file in file_format if dir_path.endswith(file)]:
                    os.startfile(dir_path)
                    library.write_log(lib_constants.LOG_INFO,"INFO: Image "
                        " opened successfully", test_case_id,script_id,
                        "None", "None", log_level, tbd)                         #if file is opened genarate pass log
                    return True
                elif [file for file in image_format if file_type.endswith(file)] or\
                [file for file in file_format if file_type.endswith(file) ]:
                    [path for path in os.walk(r'C:\\') if file_type in path ]   #searching for file in c Drive
                    os.startfile(file_type)
                    library.write_log(lib_constants.LOG_INFO,"INFO: Image "
                        "/File opened successfully", test_case_id,script_id,
                        "None", "None", log_level, tbd)                         #if file is opened genarate pass log
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Input "
                        "image\filepath is incorrect",test_case_id, script_id,
                        "None", "None",log_level, tbd)                          # write error message to log
                    return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
            test_case_id, script_id, "None", "None", log_level, tbd)            #exception error catch if failed
            return False
################################################################################





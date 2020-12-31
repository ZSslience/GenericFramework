#########################General library imports################################
import filecmp
import os
import subprocess
import sys
import time
#########################Local library imports##################################
import library
import lib_constants
import utils
################################################################################
# Function     : Compare
# Description  : Comparing Two files
# Param        : arg1= Source path of file, arg2 = Destination path of file,
#                token, test_case_id, script_id, loglevel and tbd
# Purpose      : Compares log
# Return       : Return True if no difference found after comparing two files
################################################################################


def Compare(token, test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        count = 0
        global fileOne, fileTwo
        path = lib_constants.SCRIPTDIR
        os.chdir(path)
        token1 = token.split(" ")
        log1,end_pos = utils.extract_parameter_from_token(token1, "log", "with")#Extract log 1 syntax from token
        log2,end_pos = utils.extract_parameter_from_token(token1, "with", "")   #Extract log 2 syntax from token
        step_num = int(lib_constants.LOW_BIT)

        if "step" in log1.lower():                                              #Check STEP keyword in log 1 syntax
            step_num = log1.split(" ")[-1].strip()
            if "step" in step_num.lower():
                step_num = step_num.lower().split("step")
                step_num = step_num[-1].strip()
            log1 = utils.read_from_Resultfile(step_num)                         #Read the location from given step number from result.ini file
        elif "config" in log1.lower():                                          #Check CONFIG keyword in log 1 syntax
            log1 = utils.configtagvariable(log1)                                #Extract path from Config file
        else:
            pass

        if "config" in log2.lower():                                            #Check CONFIG keyword in log 2 syntax
            log2 = utils.configtagvariable(log2)                                #Extract path from Config file
        elif "step" in log2.lower():                                            #Check STEP keyword in log 2 syntax
            step_num = log2.split(" ")[-1].strip()
            if "step" in step_num.lower():
                step_num = step_num.lower().split("step")[-1].strip()
            log2 = utils.read_from_Resultfile(step_num)                         #Read the location from given step number from result.ini file
        else:
            pass

        if 0 == os.stat(log1).st_size:                                          #Returns False when file is empty
            library.write_log(lib_constants.LOG_DEBUG, "INFO: The file for "
            "comparison is empty", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False
        elif 0 == os.stat(log2).st_size:                                        #Returns False when file is empty
            library.write_log(lib_constants.LOG_DEBUG, "INFO: The file for "
            "comparison is empty", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False
        else:
            pass

        with open(log1) as f1:
            with open(log2) as f2:
                if f1.read().upper() == f2.read().upper():
                    pass
                elif len(f1.read()) and len(f2.read()) != 0:
                    if f1.read().upper() in f2.read().upper() or \
                       f2.read().upper() in f1.read().upper():
                        pass
                else:
                    count += 1

        if 0 == count:
            library.write_log(lib_constants.LOG_INFO, "INFO: NO difference in "
            "the files", test_case_id, script_id, "None", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: The contents"
            " of the two log files are not matching", test_case_id, script_id,
            "None", "None", loglevel, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
#    Function Name   : Compare_Images()
#    Description     : Code to Compare Images.
#    Parameters      : Image1, Image2, test_case_id, script_id, loglevel and tbd
#    Purpose         : Compares images
#    Return          : True/FalseCompare image Step 4 with config-Home-Screen
################################################################################


def Compare_Images(token, test_case_id, script_id, loglevel="ALL", tbd=None):   #compare image

    try:
        a = os.getcwd()
        token1 = token.split(" ")
        image1, end_pos = utils.extract_parameter_from_token(token1, "image",
                                                             "with")            #Extract image1 details from token
        image2, end_pos = utils.extract_parameter_from_token(token1, "with", "")#Extract image2 details from token

        step_num = int(lib_constants.LOW_BIT)

        if "step" in image1.lower():                                            #Check if STEP in token
            step_num = image1.split(" ")[-1].strip()
            if "step" in step_num.lower():
                step_num = step_num.lower().split("step")
                step_num = step_num[-1].strip()
            image1 = utils.read_from_Resultfile(step_num)                       #Extract the location of the image 1 from Resultfile.ini
        elif "config" in image1.lower():                                        #Check for Config in Image 1 token
            image1 = utils.ConfigTagVariable(image1)                            #Extract image1 location from config file
        else:
            pass

        if "config" in image2.lower():                                          #Check for CONFIG in image2 token
            image2 = utils.ConfigTagVariable(image2)                            #Extract location of the image2 from the config file
        elif "step" in image2.lower():                                          #Check STEP keyword in image2 token
            step_num = image2.split(" ")[-1].strip()
            if "step" in step_num.lower():
                step_num = step_num.lower().split("step")[-1].strip()
            image2 = utils.read_from_Resultfile(step_num)                       #Extract image2 location from Result file
        else:
            pass

        image1_pixels = ""
        image2_pixels = ""
        img_perc = ""
        result = ""

                                                                                #exe_path = utils.ReadConfig("IMAGE_COMPARE","EXE_PATH")
        if os.path.isfile(image1) and os.path.isfile(image2):                   #Check files are present or not
            pass
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Specified "
            "Image Path doesn't exist.", test_case_id, script_id, "None",
            "None", loglevel, tbd)
            return False

        if run_compare_images(image1, image2, test_case_id, script_id,
                              loglevel, tbd):                                   #Start compare image which saves log in TOOLpath
            pass
        else:
            return False

        time.sleep(lib_constants.SHORT_TIME)
        os.chdir(lib_constants.TOOLPATH)
        with open("Log.txt","r") as f :                                         #File operation to search for required text
            datalines = f.readlines()
            for line in datalines:
                if "image1 Pixels" in line:
                    image1_pixels = line.split(":")[-1].strip()
                elif "image2 Pixels" in line:
                    image2_pixels = line.split(":")[-1].strip()
                elif "Percentage of Matched pixels" in line:
                    img_perc = line.split(":")[-1].strip()
                elif "Result :" in line:
                    result = line.split(":")[-1].strip()
                else:
                    pass

        os.chdir(a)
        if result != "":                                                        #If result not empty return result and Image percentage
            library.write_log(lib_constants.LOG_INFO, "INFO: Comparing Images "
            "successful with %s pixels image1, %s pixels in image2 having %s "
            "of pixels."%(image1_pixels, image2_pixels, img_perc), test_case_id,
            script_id, "None", "None", loglevel, tbd)
            return result, img_perc
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
            "Compare Images.", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False, img_perc

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : Run_Compare_Images()
# Parameters    : image 1, image 2 , test_case_id, script_id, loglevel and tbd
# Functionality : Compare image
# Return Value  : Returns true and false
################################################################################


def run_compare_images(image1, image2, test_case_id, script_id, loglevel="ALL",
                       tbd=None):

    try:
        pixel_tool = os.path.join(lib_constants.TOOLPATH,
                                  lib_constants.PIXEL_TOOL)                     #Go to tools path and save pixel.exe path

        if os.path.exists(pixel_tool):
            pass                                                                #Success
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Pixel tool "
            "not found", test_case_id, script_id, "None", "None", loglevel, tbd)
            return False

        command = (pixel_tool + " " + image1 + " " + image2)                    #Compare cmd with images path

        os.chdir(lib_constants.TOOLPATH)                                        #Change to tool directory
        result = subprocess.Popen(command, stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE)                       #Use subprocess to run the command
        time.sleep(lib_constants.SLEEP_TIME)                                    #Sleep for 15seconds

        if None != result:                                                      #If l is not none
            library.write_log(lib_constants.LOG_INFO, "INFO: Comparing Images "
            "successful, Log File Created.", test_case_id, script_id, "None",
            "None", loglevel, tbd)                                              #Success
            return True
        else:                                                                   #Else write fail in log
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Comparing "
            "Images Unsuccessful.", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", loglevel, tbd)
        return False
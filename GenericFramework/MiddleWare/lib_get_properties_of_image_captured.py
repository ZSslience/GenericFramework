__author__ = 'NARESHGX'

############################General Python Imports##############################
import cv2
import os
import time
############################Local Python Imports################################
import library
import utils
import lib_constants
################################################################################
# Function Name   : get_image_properties
# Parameters      : property, token,test_case_id,script_id,log_level, tbd
# Functionality   : to retrieve image information
# Return Value    :'Returns the image property'
# Syntax          : Get <Property> of image captured in Step <n>
################################################################################

def get_image_properties(property, token, test_case_id, script_id,
                         log_level, tbd):
    try:
        property = property.lower()
        token = token.split(' ')
        step = (library.extract_parameter_from_token(token, 'Step', '')[0]).\
            strip()
        file = utils.read_from_Resultfile(int(step))
        if os.path.exists(file):                                                # verify file exists
            library.write_log(lib_constants.LOG_INFO,"INFO: Image path exists"
                    , test_case_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Image path "
        "not found", test_case_id, script_id, "None", "None", log_level, tbd)
            return False,property, 'FAIL'
        try:
            img = cv2.imread(file)                                              # using CV2 module read image properties
            f_format = (file.split('.')[1]).upper()
            f_size = str(os.path.getsize(file)/lib_constants.ONE_KB)+'Kb'       # convert file size to Kb
            height, width, channels = img.shape                                 # get height , width and channels of image
            resolution = str(width)+" x "+str(height)
            library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Retrieved "       # debug log to print all property and value
            "property are  file type- %s,file size- %s, resolution- %s"
            %(f_format,f_size,resolution), test_case_id, script_id, "None",
                                                      "None", log_level, tbd)
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
            "retrieving image property ", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False,property, 'FAIL'
        if ('file format' in property) or ('type of file' in \
            property) or ('item type' in property) or ('file' \
                             in property) and ('size' not in property):         # to return only file format
            library.write_log(lib_constants.LOG_INFO,"INFO: Image Property %s"
            "value obtained is %s"%(property,f_format), test_case_id,
                              script_id,"None", "None",log_level, tbd)
            return True,property, f_format
        elif ('resolution' in property) or ('dimensions' in property):          # to return only resolution
            library.write_log(lib_constants.LOG_INFO,"INFO: Image Property %s"
            "value obtained is %s"%(property,resolution), test_case_id,
                              script_id,"None", "None",log_level, tbd)
            return True,property, resolution
        elif 'file size' in property:                                           # to return file size
            library.write_log(lib_constants.LOG_INFO,"INFO: Image Property %s"
            "value obtained is %s"%(property,f_size), test_case_id,
                              script_id,"None", "None",log_level, tbd)
            return True,property, f_size
        else:                                                                   # else return fail as not supported or not able to extract the parameter from image
            library.write_log(lib_constants.LOG_INFO,"INFO: Image Property not"
        " supported", test_case_id, script_id, "None", "None", log_level, tbd)
            return False,property, 'FAIL'
    except Exception as e:                                                      # if exception found then return fail
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in fetching"
    "Image property"%e, test_case_id, script_id,"None","None", log_level, tbd)
        return False,property, 'FAIL'
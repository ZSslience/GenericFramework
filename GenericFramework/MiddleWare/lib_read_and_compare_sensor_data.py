__author__ = r'tnaidux'

# Global python Imports
import os
import subprocess
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_sensorviewer


def read_and_compare_sensor_data(original_string, sensor_name, tool, 
                                 test_case_id, script_id, log_level, tbd):
    
    try:
        sensor_status = lib_sensorviewer.\
            get_sensor_status(sensor_name, test_case_id, script_id, tool,
                              log_level, tbd)

        if sensor_status is "Ready":
            library.write_log(lib_constants.LOG_INFO, "INFO: %s sensor status "
                              "is %s" % (sensor_name, sensor_status),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s sensor "
                              "status is not %s" % (sensor_name,
                                                    sensor_status),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        sensor_unique_id_list = {key.upper().strip(): value for key, value in
                                 list(lib_constants.SENSORDICT.items())}
        sensor_unique_id = sensor_unique_id_list.get(sensor_name.upper(), None)
        
        if write_sensor_data_to_result_folder(sensor_name, sensor_unique_id,
                                              tool, test_case_id, script_id,
                                              log_level, tbd):
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is verified "
                              "successfully" % original_string, test_case_id, 
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is "
                              "verification failed" % original_string, 
                              test_case_id, script_id, "None", "None", 
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, 
                          test_case_id, script_id, "None", "None", log_level, 
                          tbd)
        return False


def write_sensor_data_to_result_folder(sensor_name, sensor_unique_id, tool,
                                       test_case_id, script_id,
                                       log_level="ALL", tbd=None):

    try:
        result_dict = lib_sensorviewer.\
            result_data(sensor_name, sensor_unique_id, tool, test_case_id,
                        script_id, log_level, tbd)

        if not result_dict:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "perform the read and compare sensor data",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            if not os.path.exists(lib_constants.SCRIPTDIR):
                os.mkdir(lib_constants.SCRIPTDIR)

            complete_name = os.path.join(lib_constants.SCRIPTDIR + "/%s.txt"
                                         % (test_case_id + '_' + sensor_name))

            with open(complete_name, "w") as f:
                for key, val in result_dict.items():
                    f.writelines(key + ":" + val + "\n")

            library.write_log(lib_constants.LOG_INFO, "Successfully wrote the "
                              "%s sensor data and values in the file"
                              % sensor_name, test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

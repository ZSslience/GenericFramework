__author__ = r"tnaidux\yusufmox"

# Local Python Imports
import lib_constants
import library
import lib_sensorviewer

################################################################################
# Function Name : read_status_from_sensor_tool
# Parameters    : sensor_name, tc_id, script_id, log_level, tbd
# Functionality : executes the command to verify the sensor status by using
#                 sensor viewer tool
# Return Value  : returns True for success, False otherwise
################################################################################


def read_status_from_sensor_tool(sensor_name, status, tc_id, script_id,
                                 log_level="ALL", tbd=None):

    try:
        sensor_status = lib_sensorviewer.\
            get_sensor_status(sensor_name, tc_id, script_id, "SensorViewer")

        if status is False:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the status of %s" % sensor_name, tc_id,
                              script_id, "SensorViewer", "None", log_level, tbd)
            return False
        elif sensor_status.upper() == status.upper():
            library.write_log(lib_constants.LOG_INFO, "INFO: current status "
                              "of %s is %s" % (sensor_name, sensor_status),
                              tc_id, script_id, "SensorViewer", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Status of "
                              "%s is %s" %(sensor_name, sensor_status), tc_id,
                              script_id, "SensorViewer", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s " % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

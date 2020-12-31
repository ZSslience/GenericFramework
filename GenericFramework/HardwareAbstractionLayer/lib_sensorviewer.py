__author__ = r"yusufmox"

# Global Python Imports
import csv
# import dircache
import os
import shutil
import subprocess
import time


# Local Python Imports
import lib_constants
import library
import utils

win_rt_sensor_list = ["ALTIMETER SENSOR", "DEVICE ORIENTATION SENSOR"]

################################################################################
# Function Name : get_sensor_status
# Parameters    : sensor_name, test_case_id, script_id, log_level, tool, tbd
# Functionality : gets the current status of the sensor given
# Return Value  : returns status for success, False otherwise
################################################################################


def get_sensor_status(sensor_name, test_case_id, script_id, tool,
                      log_level="ALL", tbd=None):

    try:
        sensor_xml = sensor_name.upper().split("SENSOR")[0].strip() + ".xml"
        if " " in sensor_xml:
            sensor_xml = sensor_xml.replace(" ", "-")
        tool_path = lib_constants.TOOLPATH + os.sep + "SensorViewer"
        cwd = os.getcwd()

        os.chdir(tool_path)
        for root, dirs, files in os.walk(tool_path):
            for temp in dirs:
                if "log_" in temp:
                    shutil.rmtree(temp)

        if os.path.exists(sensor_xml):
            library.write_log(lib_constants.LOG_INFO, "INFO: Removing the "
                              "existing file %s" % sensor_xml, test_case_id, script_id,
                              tool, "None", log_level, tbd)
            os.remove(sensor_xml)
        if sensor_name.upper() in win_rt_sensor_list:
            gen_config_cmd = 'SensorViewer.exe -createConfig ' + sensor_xml + \
                             ' -apiType "Windows RT for Win10 API"'
            edit_lines = 6
            luid_line = 1

        elif 'CONFIG-' in sensor_name:
            tag = sensor_name.split('-')[1].strip()
            value = sensor_name.split('-')[2].strip()
            sensor_name = utils.ReadConfig(tag,value)
            gen_config_cmd = 'SensorViewer.exe -createConfig ' + sensor_xml + \
                             ' -apiType "Desktop API"'
            edit_lines = 8
            luid_line = 7

        else:
            gen_config_cmd = 'SensorViewer.exe -createConfig ' + sensor_xml + \
                ' -apiType "Desktop API"'
            edit_lines = 8
            luid_line = 7

        library.write_log(lib_constants.LOG_INFO, "INFO: Command to generate "
                          "config xml file for sensor is:\n%s" % gen_config_cmd,
                          test_case_id, script_id, tool, "None", log_level, tbd)

        result = os.system(gen_config_cmd)
        time.sleep(20)

        if result != 0:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "execute command %s" % gen_config_cmd, test_case_id,
                              script_id, tool, "None", log_level, tbd)
            return False
        else:
            try:
                if sensor_name in win_rt_sensor_list:
                    luid = lib_constants.SENSORUIDDICT[sensor_name.upper()]
                else:
                    luid = lib_constants.SENSORDICT[sensor_name.upper()]

            except Exception as e:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: LUID "
                                  "of sensor %s is not available in "
                                  "lib_constants.SENSORDICT", test_case_id, script_id,
                                  tool, "None", log_level, tbd)
                return False

            with open(sensor_xml, "r") as _f:
                data = _f.readlines()

            i = 0
            with open(sensor_xml, "w") as f_:
                while i != len(data):
                    if "<SensorConfig>" in data[i] and\
                            luid in data[i + luid_line]:
                        for j in range(edit_lines):
                            if "false" in data[i]:
                                f_.write(data[i].replace("false", "true"))
                            else:
                                f_.write(data[i])
                            i = i + 1

                    if "<IsLoggingEnabled>" in data[i] and "false" in data[i]:
                        f_.write(data[i].replace("false", "true"))
                        i = i + 1
                    else:
                        f_.write(data[i])
                        i = i + 1

            get_status_cmd = "SensorViewer.exe -timeout 15 -config " + \
                sensor_xml

            library.write_log(lib_constants.LOG_INFO, "INFO: Command to get "
                              "sensor status is:\n%s" % get_status_cmd, test_case_id,
                              script_id, tool, "None", log_level, tbd)

            status_result = os.system(get_status_cmd)
            time.sleep(20)

            if status_result != 0:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to execute command %s" % get_status_cmd,
                                  test_case_id, script_id, tool, "None", log_level,
                                  tbd)
                return False
            else:
                for dirname in os.listdir(tool_path):
                    if dirname.startswith("log_"):
                        logpath = os.path.join(tool_path, dirname)

                if os.path.exists(logpath):                                     # Verified the  log path of Sensor Viewer & continue the execution
                    library.write_log(lib_constants.LOG_INFO, "INFO: Log "
                                      "generated successfully for %s using "
                                      "Sensor Viewer Tool.\nSensor Viewer Log "
                                      "Path: %s" % (sensor_name, logpath),
                                      test_case_id, script_id, tool, "None",
                                      log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to generate the Log for %s using"
                                      " Sensor Viewer Tool." % sensor_name,
                                      test_case_id, script_id, tool, "None",
                                      log_level, tbd)
                    os.chdir(cwd)
                    return False

                os.chdir(logpath)
                dirlist = dircache.listdir(logpath)                             # To get the list of file
                time.sleep(10)
                count = 0
                flag = False

                for i in dirlist:
                    if ".csv".upper() in i.upper():
                        count = count + 1
                        shutil.copy(i, cwd)
                        with open(i, 'r') as fp:
                            reader = csv.reader(fp)
                            if "DEVICE ORIENTATION SENSOR" != sensor_name:
                                for row in reader:
                                    if row[1] != 0 and row[1] != None:
                                        flag = True
                                    else:
                                        flag = False
                            else:
                                for row in reader:
                                    if row[0] != 0 and row[0] != None:
                                        flag = True
                                    else:
                                        flag = False

                os.chdir(cwd)
                status = False

                if flag == True:
                    if 1 == count:
                        status = "Ready"                                        # If sensors contains the data in log file, then verified
                    else:
                        return False
                else:
                    status = "Error"
                return status
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s " % e,
                          test_case_id, script_id, "None", "None", log_level, tbd)
        return False

def get_sensor_val(sensor_name, test_case_id, script_id, tool, log_level="ALL",
                      tbd=None):
    try:
        sensor_xml = sensor_name.split(" ")[0] + ".xml"
        tool_path = lib_constants.TOOLPATH + os.sep + "SensorViewer"
        cwd = os.getcwd()

        os.chdir(tool_path)
        for root, dirs, files in os.walk(tool_path):
            for temp in dirs:
                if "log_" in temp:
                    shutil.rmtree(temp)

        if os.path.exists(sensor_xml):
            library.write_log(lib_constants.LOG_INFO, "INFO: Removing the "
                              "existing file %s" % sensor_xml, test_case_id, script_id,
                              tool, "None", log_level, tbd)
            os.remove(sensor_xml)

        gen_config_cmd = 'SensorViewer.exe -x ' + sensor_xml + \
                         ' -a "Desktop API"'

        library.write_log(lib_constants.LOG_INFO, "INFO: Command to generate "
                          "config xml file for sensor is:\n%s" % gen_config_cmd,
                          test_case_id, script_id, tool, "None", log_level, tbd)

        result = os.system(gen_config_cmd)
        time.sleep(20)

        if result != 0:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "execute command %s" % gen_config_cmd, test_case_id,
                              script_id, tool, "None", log_level, tbd)
            return False
        else:
            try:
                luid = lib_constants.SENSORDICT[sensor_name.upper()]
            except Exception as e:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: LUID "
                                 "of sensor %s is not available in "
                                 "lib_constants.SENSORDICT", test_case_id, script_id,
                                  tool, "None", log_level, tbd)
                return False

            with open(sensor_xml, "r") as _f:
                data = _f.readlines()

            i = 0
            with open(sensor_xml, "w") as f_:
                while i != len(data):
                    if "<SensorConfig>" in data[i] and luid in data[i + 7]:
                        for j in range(8):
                            if "false" in data[i]:
                                f_.write(data[i].replace("false", "true"))
                            else:
                                f_.write(data[i])
                            i = i + 1

                    if "<IsLoggingEnabled>" in data[i] and "false" in data[i]:
                        f_.write(data[i].replace("false", "true"))
                        i = i + 1
                    else:
                        f_.write(data[i])
                        i = i + 1

            get_status_cmd = "SensorViewer.exe -timeout 15 -config " + \
                             sensor_xml

            library.write_log(lib_constants.LOG_INFO, "INFO: Command to get "
                              "sensor status is:\n%s" % get_status_cmd, test_case_id,
                              script_id, tool, "None", log_level, tbd)

            status_result = os.system(get_status_cmd)
            time.sleep(20)
            if status_result != 0:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to execute command %s" % get_status_cmd,
                                  test_case_id, script_id, tool, "None", log_level,
                                  tbd)
                return False
            else:
                for dirname in os.listdir(tool_path):
                    if dirname.startswith("log_"):
                        logpath = os.path.join(tool_path, dirname)

                if os.path.exists(logpath):                                     # Verified the  log path of Sensor Viewer & continue the execution
                    library.write_log(lib_constants.LOG_INFO, "INFO: Log "
                                      "generated successfully for %s using "
                                      "Sensor Viewer Tool.\nSensor Viewer Log "
                                      "Path: %s" % (sensor_name, logpath),
                                      test_case_id, script_id, tool, "None",
                                      log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                     "Failed to generate the Log for %s using"
                                     " Sensor Viewer Tool." % sensor_name,
                                      test_case_id, script_id, tool, "None",
                                      log_level, tbd)
                    os.chdir(cwd)
                    return False

                os.chdir(logpath)
                dirlist = dircache.listdir(logpath)                             # To get the list of file
                time.sleep(10)
                count = 0
                flag = False

                for i in dirlist:
                    if ".csv".upper() in i.upper():
                        count = count + 1
                        shutil.copy(i, cwd)
                        with open(i, 'r') as fp:
                            reader = csv.reader(fp)
                            flag = False
                            for row in reader:
                                if row[3] != 0 and row[3] != None and flag == False:
                                    flag = True
                                elif flag is True:
                                    return row[3]

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s " % e,
                          test_case_id, script_id, "None", "None", log_level, tbd)
        return False


def result_data(sensor_name, sensor_unique_id, tool, test_case_id, script_id,
                log_level="ALL", tbd=None):
    
    try:
        value = []
        result_file_path = \
            sensor_viewer_tool_execution(sensor_name, sensor_unique_id,
                                         tool, test_case_id, script_id,
                                         log_level, tbd)

        if not result_file_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "communicate with the %s sensor" % sensor_name,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            with open(result_file_path, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                data = next(csv_reader)

                for row in csv_reader:
                    value.append(row)

            result_values = value[0]
            result_dict = dict(zip(data, result_values))

            for i in range(len(data)):
                library.write_log(lib_constants.LOG_INFO, "%s: %s"
                                  % (str(data[i]), str(result_values[i])),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully got "
                              "the %s sensor data and values" % sensor_name,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return result_dict
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def sensor_viewer_tool_execution(sensor_name, sensor_unique_id, tool,
                                 test_case_id, script_id, log_level="ALL",
                                 tbd=None):

    try:
        if not os.path.exists(lib_constants.TOOLPATH + os.sep + "SensorViewer"):
            library.write_log(lib_constants.LOG_WARNING, "WARNING: SensorViewer"
                              " Folder is not present", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:
            config_name = \
                create_sensor_viewer_config_xml(sensor_name, sensor_unique_id,
                                                tool, test_case_id, script_id,
                                                log_level, tbd)

            sensor_viewer_cmd = "%s -t=30 -config=\"%s\""
            tool_sensor_viewer_exe = r"SensorViewer.exe"
            cmd = sensor_viewer_cmd % (tool_sensor_viewer_exe, config_name)

            os.chdir(lib_constants.TOOLPATH + os.sep + "SensorViewer")
            result = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            output = result.communicate()[0]
            returncode = int(result.returncode)

            if 0 == returncode:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command "
                                  "execution succesfull %s" %cmd, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                reg_exp = r"log_\d\d_\d\d_\d\d_\d\d_\d\d_\d\d"                  # fetching the output file using regular expression
                result_output = process.stdout
                output_file_name = str(re.findall(reg_exp, str(result_output))[0])
                output_file_path = \
                    r"%s\\%s\\" % (lib_constants.SENSOR_VIEWER_PATH,              # fetching the output file name
                                            output_file_name)
            else:
                utils.write_log(lib_constants.LOG_ERROR,
                                "Command execution failed %s " % cmd,
                                test_case_id,
                                script_id,
                                tools,
                                lib_constants.STR_NONE,
                                log_level,
                                opt)
                return False
            if sensor_name == GYROMETER:
                csv_result = RES_GYROMETER_CSV
            elif sensor_name == PHYSICAL_ACCELEROMETER:
                csv_result = RES_PHYSICAL_ACCELEROMETER_CSV
            elif sensor_name == MAGNETOMETER:
                csv_result = RES_MAGNETOMETER_CSV
            else:
                csv_result = RES_DEFAULT % sensor_name
            result_file_path = os.path.join(output_file_path+csv_result)
            if not os.path.exists(result_file_path):
                utils.write_log(lib_constants.LOG_ERROR,
                                "Error occurred while performing action Read "
                                "data for sensor: %s .Message: Unable to "
                                "read data from sensor %s Polling stopped"
                                % (sensor_name, sensor_name),
                                test_case_id,
                                script_id,
                                tools,
                                lib_constants.STR_NONE,
                                log_level,
                                opt)
                return False
            else:
                utils.write_log(lib_constants.LOG_INFO,
                                " %s Sensor is working" %
                                sensor_name,
                                test_case_id,
                                script_id,
                                tools,
                                lib_constants.STR_NONE,
                                log_level,
                                opt)
                return result_file_path
    except Exception as ex:
        utils.write_log(lib_constants.LOG_ERROR,
                        "Exception %s " % str(ex),
                        test_case_id,
                        script_id,
                        tools,
                        lib_constants.STR_NONE,
                        log_level,
                        opt)
        return False

def create_sensor_viewer_config_xml(sensor_name, unique_sensor_id, tc_id,
                                    script_id, target_os, tools,
                                    log_level="ALL", opt=None):
    """
        Function Name     : create_sensor_viewer_config_xml
        Parameters        : sensor_name, sensor_name, unique_sensor_id, tc_id,
                            script_id,target_os,  tools, log_level, opt
        Functionality     : To execute Sensor Viewer tools
        Functions Invoked : xml_create_tag_section(),xml_create_value_section()
        Return Value      : File Path(String)/ False
    """
    working_dir = os.getcwd()
    script_file = os.path.join(working_dir,
                               "config_%s.xml" % sensor_name)
    utils.write_log(lib_constants.LOG_INFO,
                    "Creating XML setting file",
                    tc_id,
                    script_id,
                    tools,
                    lib_constants.STR_NONE,
                    log_level,
                    opt)
    root = Et.Element(MAINCONFIG)
    api_type = xml_create_tag_section(root, API_TYPE)                           # compileing the xml file
    xml_create_value_section(api_type, None, WINDOWS_TEN)
    sensor_element = xml_create_tag_section(root, SENSORS)
    sensor_config = xml_create_tag_section(sensor_element, SENSOR_CONFIG)
    unique_id = xml_create_tag_section(sensor_config, UNIQUE_ID)
    xml_create_value_section(unique_id, None, unique_sensor_id)
    s_name = xml_create_tag_section(sensor_config, NAME)
    xml_create_value_section(s_name, None, sensor_name)
    is_selected = xml_create_tag_section(sensor_config, IS_SELECTED)
    xml_create_value_section(is_selected, None, lib_constants.STR_TRUE)
    is_polling = xml_create_tag_section(sensor_config, IS_POLLING)
    xml_create_value_section(is_polling, None, lib_constants.STR_TRUE)
    is_streaming = xml_create_tag_section(sensor_config, IS_STREAMING)
    xml_create_value_section(is_streaming, None, lib_constants.STR_TRUE)
    xml_create_tag_section(sensor_config, DISABLED_AXES)
    properties = xml_create_tag_section(sensor_config, PROPERTIES)
    primitive_property_config(properties,
                              PRIMITIVE_PROPERTY_CONFIG_OF_UINT_THIRTY_TWO,
                              REPORT_INTERVAL, FIFTY)
    primitive_property_config(properties, PRIMITIVE_PROPERTY_CONFIG_OF_STRING,
                              READING_TRANSFORM,
                              lib_constants.STR_NONE)
    primitive_property_config(properties,
                              PRIMITIVE_PROPERTY_CONFIG_OF_UINT_THIRTY_TWO,
                              POLLING_INTERVAL, FIVE_HUNDRED)
    plot = xml_create_tag_section(sensor_config, PLOT)
    xml_create_tag_section(plot, DISABLED_AXES_IN_CHART)
    logging_config = xml_create_tag_section(root, LOGGING_CONFIG)
    is_logging_enabled = xml_create_tag_section(logging_config,
                                                IS_LOGGING_ENABLED)
    xml_create_value_section(is_logging_enabled, None, lib_constants.STR_TRUE)
    tree = Et.ElementTree(root)
    tree.write(script_file)
    if os.path.isfile(script_file):
        utils.write_log(lib_constants.LOG_INFO,
                        "XML file for SensorViewer Tool Successfully Created",
                        tc_id,
                        script_id,
                        tools,
                        lib_constants.STR_NONE,
                        log_level,
                        opt)
        return script_file
    else:
        utils.write_log(lib_constants.LOG_ERROR,
                        "XML file for SensorViewer Tool failed to create",
                        tc_id,
                        script_id,
                        tools,
                        lib_constants.STR_NONE,
                        log_level,
                        opt)
        return False
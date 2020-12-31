__author__ = "tnaidux"

# Global Python Imports
import os
import sys
import time

# Local Python Imports
import lib_constants
import library
import utils


def run_bkm_test_case(test_case_id, script_id, test_case_number,
                      log_level="ALL", tbd=None):
    try:
        bkm_tc_package_path = r"C:\Testing\GenericFramework\bkm_tcs_package"

        for root, dirs, files in os.walk(bkm_tc_package_path):
            for temp in files:
                if str(test_case_number) in str(temp):
                    test_case_number_path = os.path.join(root, temp)

        print(test_case_number_path)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
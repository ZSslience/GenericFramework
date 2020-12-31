"""
State defines all the possible environment and power state
"""

#from common2.lib.private import sparklogger
import json
import os
import library
import lib_constants

POWER_STATE_S0 = r'S0'
POWER_STATE_S3 = r'S3'
POWER_STATE_S4 = r'S4'
POWER_STATE_S5 = r'S5'
POWER_STATE_G3 = r'G3'

ENV_STATE_EFISHELL = r'EFIShell'
ENV_STATE_BIOS_BOOT_MENU = r'BIOS_BOOT_MENU'
ENV_STATE_BIOS_SETUP_MENU = r'BIOS_SETUP_MENU'
ENV_STATE_ENTRY_MENU = r'EntryMenu'
ENV_STATE_WINDOWS = r'Windows'
ENV_STATE_NANO = r'Nano'
ENV_STATE_LINUX = r'Linux'
ENV_STATE_SIMICS = r'Simics'
ENV_STATE_PXE = r'PXE'
ENV_STATE_BIOS_UI = 'BIOS_UI'

# Unknown can be valid both for env and power state
STATE_Unknown = r'Unknown'
# NA status is only valid for env state while power state is in S5/G3/S4
STATE_NotAvailable = r'NA'

def get_environment_state():
    """
        get current environment state from previous set state result which can be a file or environment variable.

        :return: current environment state
                ENV_STATE_BIOS_SETUP_MENU/ENV_STATE_BIOS_BOOT_MENU/ENV_STATE_EFISHELL/ENV_STATE_ENTRY_MENU

                /ENV_STATE_WINDOWS/ENV_STATE_LINUX/STATE_Unknown/STATE_NotAvailable

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'state.tmp')
    try:
        fd = open(state_file_path, mode='r')
        dict_env_power_state = json.JSONDecoder().decode("".join(fd.readlines()))
        fd.close()
        return STATE_Unknown if not dict_env_power_state['EnvState'] else dict_env_power_state['EnvState']
    except Exception as ex:
        library.write_log(lib_constants.LOG_DEBUG, r'%s:get_environment_state' % ex.message, "None", "None",
                          "None", "None", "None", "None")
        return STATE_Unknown

def get_simic_power_state():
    """
        get current power state from previous set state result which can be a file or environment variable.

        if the temp file is null, return S0.

        :return: current simics power state POWER_STATE_S0/POWER_STATE_S5/POWER_STATE_G3

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'state.tmp')
    try:
        fd = open(state_file_path, mode='r')
        dict_env_power_state = json.JSONDecoder().decode("".join(fd.readlines()))
        fd.close()
        return POWER_STATE_S0 if not dict_env_power_state['PowerState'] else dict_env_power_state['PowerState']
    except Exception as ex:
        library.write_log(lib_constants.LOG_DEBUG, r'%s:get_simic_power_state' % ex.message, "None", "None",
                          "None", "None", "None", "None")
        return POWER_STATE_S0

def check_state_available(state):
    """
    This API will used to check the state is accessible or not on DUT

    :param:     State: Object including env_state and power_state

    :return:    True/False

    :black box valid equivalent class:
                                        State = State(ENV_STATE_EFISHELL,POWER_STATE_S0),

                                        State(ENV_STATE_BIOS_BOOT_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_BIOS_SETUP_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_ENTRY_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_WINDOWS,POWER_STATE_S0),

                                        State(ENV_STATE_WINDOWS,POWER_STATE_S3),

                                        State(ENV_STATE_LINUX,POWER_STATE_S0),

                                        State(ENV_STATE_LINUX,POWER_STATE_S3),

                                        State(STATE_NotAvailable,POWER_STATE_S4),

                                        State(STATE_NotAvailable,POWER_STATE_S5),

                                        State(STATE_NotAvailable,POWER_STATE_G3),

                                        State(STATE_Unknown,POWER_STATE_S0),

                                        State(STATE_Unknown,POWER_STATE_S3),

                                        State(STATE_Unknown,POWER_STATE_S4),

                                        State(STATE_Unknown,POWER_STATE_S5),

                                        State(STATE_Unknown,POWER_STATE_G3),

                                        State(STATE_Unknown,STATE_Unknown),

                                        State(ENV_STATE_SIMICS,POWER_STATE_S0),

                                        State(ENV_STATE_NANO, POWER_STATE_S0)
    :black box invalid equivalent class:
                                        State = State(ENV_STATE_WINDOWS,POWER_STATE_S5),

                                        State(ENV_STATE_LINUX,POWER_STATE_G3)

    estimated LOC = 10
    """
    if (state.env_state, state.power_state) not in [(ENV_STATE_EFISHELL, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_BOOT_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_SETUP_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_ENTRY_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_WINDOWS, POWER_STATE_S0),
                                                    (ENV_STATE_WINDOWS, POWER_STATE_S3),
                                                    (ENV_STATE_LINUX, POWER_STATE_S0),
                                                    (ENV_STATE_LINUX, POWER_STATE_S3),
                                                    (STATE_NotAvailable, POWER_STATE_S4),
                                                    (STATE_NotAvailable, POWER_STATE_S5),
                                                    (STATE_NotAvailable, POWER_STATE_G3),
                                                    (STATE_Unknown, POWER_STATE_S0),
                                                    (STATE_Unknown, POWER_STATE_S3),
                                                    (STATE_Unknown, POWER_STATE_S4),
                                                    (STATE_Unknown, POWER_STATE_S5),
                                                    (STATE_Unknown, POWER_STATE_G3),
                                                    (STATE_Unknown, STATE_Unknown),
                                                    (ENV_STATE_NANO, POWER_STATE_S0),
                                                    (ENV_STATE_SIMICS, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_UI, POWER_STATE_S0)]:
        return False
    return True

class State(object):
    """
    SUT State:
        including environment state and power state

        all definitions are in above state code
    """

    def __init__(self, env_state, power_state):
        """
        initialize env state power state

        :param: env_state: env state

        :param: power_state: power state

        :return:

        :black box valid equivalent class: env_state, power_state is None

        :black box valid equivalent class: env_state,power_state is not None

        estimated LOC = 5
        """
        self.env_state = env_state
        self.power_state = power_state


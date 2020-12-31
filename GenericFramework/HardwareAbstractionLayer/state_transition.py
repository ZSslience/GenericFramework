"""
Support SUT to gracefully finish the state change with action accordingly
No implicit transition supported in this module.
"""
from state import check_state_available
from return_code import *
import library
import lib_constants
from state import get_environment_state, get_simic_power_state, State, STATE_Unknown
from configuration import get_value
import os
import json

class StateTransition(object):
    """
    :State Transition:
        support SUT to gracefully change the state by correctly action

        If user implement the state transition in case level, need to call setstate() to return the state back.

        Also user can call get_state() to get current environment state and power state.
    """
    def get_state(self):
        """
        get current state including environment and power state. This function is for external call.

        if it is presilcon, we get the power state from status file which is same as env_state.

        :return: current state(EnvState, PowerState)

        :dependency:
            private.state_transition.get_environment_state()

            private.state_transition.get_simics_power_state()

            private.controlbox_hal get_power_state()

            Configuration.get_value(SUT,silicon)

        :black box equivalent class:
            get_environment_state()=
                state.ENV_STATE_SIMICS,

                state.ENV_STATE_BIOS_SETUP_MENU,

                state.ENV_STATE_BIOS_BOOT_MENU,

                state.ENV_STATE_EFISHELL,

                state.ENV_STATE_ENTRY_MENU,

                state.ENV_STATE_WINDOWS,

                state.ENV_STATE_LINUX,

                state.STATE_Unknown,

                state.STATE_NotAvailable;

            get_power_state()=
                state.POWER_STATE_S0,

                state.POWER_STATE_S3,

                state.POWER_STATE_S4,

                state.POWER_STATE_S5,

                state.POWER_STATE_G3,

                state.STATE_Unknown

            Configuration.get_value(SUT,silicon)=PreSillicon/PostSillicon

            get_simics_power_state()=
                state.POWER_STATE_S0,

                state.POWER_STATE_S3,

                state.POWER_STATE_S4,

                state.POWER_STATE_S5

        estimated LOC = 10
        """
        get_silicon = os.getenv('SUT.silicon') if os.getenv('SUT.silicon') else get_value('Platform Info', 'silicon')
        library.write_log(lib_constants.LOG_DEBUG,'get_silicon = {0}'.format(get_silicon),"None", "None","None", "None", "None", "None")
        if get_silicon == 'PreSilicon':
            return State(get_environment_state(), get_simic_power_state())
        else:
            try:
                power_state_detection = os.getenv("SUT.power_state_detection")
            except Exception as ex:
                library.write_log(lib_constants.LOG_DEBUG, 'get power_state_detection error ex={0}'.format(ex), "None", "None",
                                  "None", "None", "None", "None")
                power_state_detection = 'Enable'

            if power_state_detection == "Disable":
                state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.tmp')
                try:
                    fd = open(state_file_path, mode='r')
                    dict_env_power_state = json.JSONDecoder().decode("".join(fd.readlines()))
                    fd.close()
                    power_state = STATE_Unknown if not dict_env_power_state['PowerState'] else dict_env_power_state['PowerState']
                    return State(get_environment_state(), power_state)
                except Exception as ex:
                    library.write_log(lib_constants.LOG_DEBUG, r'%s:get_simic_power_state' % ex.message,
                                      "None", "None","None", "None", "None", "None")
                    return State(get_environment_state(), STATE_Unknown)
            else:
                return State(get_environment_state(), STATE_Unknown)

            # return State(get_environment_state(), get_sut_power_state())
        # if 1:
        #     return State(get_environment_state(), get_power_state())
        # else:
        #     return State(get_environment_state(), get_simic_power_state())

    def set_state(self, state):
        """
        set current state to a file or environment variable.This function is for external call.

        :param state: state instance (state(env_state, power_state))

        :return:
            SUCCESSFUL: set successfully

            RET_ENV_FAIL: set state failed.

            RET_INVALID_INPUT: input state is wrong

        :dependency API: State.check_state_available(State)

        :black box equivalent class:
                                    state =
                                            State(ENV_STATE_EFISHELL,POWER_STATE_S0),

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

                                            State(ENV_STATE_WINDOWS,POWER_STATE_S5),

                                            State(ENV_STATE_LINUX,POWER_STATE_G3);

                                    check_state_available = True/False

        estimated LOC = 10
        """
        if not check_state_available(state):
           return RET_INVALID_INPUT

        dict_env_power_state = {'EnvState': state.env_state, 'PowerState': state.power_state}
        state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.tmp')

        try:
            fd = open(state_file_path, mode='w+')
            json_state = json.JSONEncoder().encode(dict_env_power_state)
            fd.write(json_state)
            fd.close()
        except Exception as ex:
            library.write_log(lib_constants.LOG_DEBUG, r'%s:_set_state' % ex.message,"None", "None", "None", "None", "None", "None")
            return RET_ENV_FAIL

        return RET_SUCCESS


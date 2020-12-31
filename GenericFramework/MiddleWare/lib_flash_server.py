import time
import os
from SoftwareAbstractionLayer import library
from SoftwareAbstractionLayer import lib_constants
from MiddleWare import lib_power_action_soundwave


def write_log(level, msg):
    library.write_log(level, msg)


def flash_cpld(path, soundwave_port='COM101', binary=None, jtag_binary=None, expect_cables=None, regex_device='10M',
               abort_on_failure=False):
    from HardwareAbstractionLayer import Quartus

    q = Quartus.Quartus(path, binary, jtag_binary)
    retry = 0
    while True:
        if retry > 3:
            write_log(lib_constants.LOG_ERROR, 'Failed to detect devices as trying 3 times')
            return False
        write_log(lib_constants.LOG_INFO, 'Try {} time to flash cpld'.format(retry + 1))
        lib_power_action_soundwave.ac_off(soundwave_port)
        lib_power_action_soundwave.ac_on(soundwave_port)
        if q.detect_devices(expect_cables, regex_device):
            if q.program_cpld(abort_on_failure):
                write_log(lib_constants.LOG_INFO, 'Success to flash cpld')
                return True
        retry += 1


def flash_bmc(bmc, binary=None, soundwave_port='COM101'):
    if not os.path.exists(bmc):
        write_log(lib_constants.LOG_ERROR, 'bmc file does not exist')
        return False
    from HardwareAbstractionLayer import sf600
    lib_power_action_soundwave.dc_off(soundwave_port)
    time.sleep(2)
    lib_power_action_soundwave.ac_off(soundwave_port)
    sf = sf600.SF600(binary)
    if sf.burn(bmc):
        write_log(lib_constants.LOG_INFO, 'Success to flash bmc')
        return True
    else:
        write_log(lib_constants.LOG_ERROR, 'Failed to flash bmc')
        return False


def flashifwi_em100(binfile, soundwave_port='COM101', chip_name="MX25L51245G", finish_stop=False, binary=None):
    """
    This API will set the Binfile to the EM100 class and call the funtion burn from the EM100 class.
    :param:   binfile            :IFWI bin file name with full path.
    :return:  RET_SUCCESS        :Successfully flashed IFWI bin file was emulated.
              RET_TEST_FAIL      :After flashing, chip content checksum is
               not correct or depended APIs return RET_TEST_FAIL;
              RET_INVALID_INPUT  :If the binfile is not correct or not exist.
    :external dependence:   private/EM100(); private/EM100().setBios; private/EM100().burn()
    :black box equivalent class
        valid equivalent Class:   binfile=PLYDCRB.86B.OR.64.2016.33.4.07.0636_LBG_SPS.bin
        invalid equivalent Class: binfile=None
    :estimated LOC:  9
    """
    if not os.path.exists(binfile):
        write_log(lib_constants.LOG_ERROR, 'ifwi bin file does not exist')
        return False
    from HardwareAbstractionLayer import EM100
    lib_power_action_soundwave.dc_off(soundwave_port)
    time.sleep(2)
    lib_power_action_soundwave.ac_off(soundwave_port)
    write_log(lib_constants.LOG_INFO, 'Current bin file: %s' % binfile)
    em100 = EM100.EM100(binary)
    em100.setChip(chip_name)
    if em100.setBios(binfile):
        write_log(lib_constants.LOG_INFO, 'Flashing IFWI Start')
        if em100.burn():
            write_log(lib_constants.LOG_INFO, 'Flashing IFWI Done')
            if finish_stop:
                em100.stop()
            return True
        else:
            write_log(lib_constants.LOG_ERROR, 'Unable to flash the BIOS bin file')
            return False
    else:
        write_log(lib_constants.LOG_ERROR, 'Unable to set the BIOS name')
        return False

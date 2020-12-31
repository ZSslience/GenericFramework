import time
from SoftwareAbstractionLayer import library
from SoftwareAbstractionLayer import lib_constants
from HardwareAbstractionLayer import soundwave


def write_log(level, msg):
    library.write_log(level, msg)


def get_soundwave_instance(soundwave_port):
    return soundwave.SoundWave(soundwave_port)


def ac_on(soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        result = sd.ac_power_on()
        time.sleep(15)
        if result == lib_constants.LOG_PASS and get_power_status(soundwave_port, sd) != 'G3':
            write_log(lib_constants.LOG_INFO, 'ac power on SUT action is successful')
            return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'ac power off SUT action is failed')
    return False


def ac_off(soundwave_port='COM101', retry=10):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        result = sd.ac_power_off()
        time.sleep(5)
        if result == lib_constants.LOG_PASS and get_power_status(soundwave_port, sd) == 'G3':
            voltage = sd.get_ad_values([2, 11])
            main_pw = round(voltage[0], 5)
            p3v3_pw = round(voltage[1], 5)
            if main_pw == 0.0 and p3v3_pw == 0.0:
                write_log(lib_constants.LOG_INFO, 'ac power off SUT action is successful')
                return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'ac power off SUT action is failed')
    return False


def dc_on(soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        if sd.press_power_button():
            time.sleep(3)
            result = sd.release_power_button()
            time.sleep(5)
            if result:
                write_log(lib_constants.LOG_INFO, 'dc power on SUT action is successful')
                return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'dc power on SUT action is failed')
    return False


def dc_off(soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        if sd.press_power_button():
            time.sleep(5)
            result = sd.release_power_button()
            time.sleep(5)
            if result:
                write_log(lib_constants.LOG_INFO, 'dc power off SUT action is successful')
                return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'dc power off SUT action is failed')
    return False


def usb_to_host(soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        if sd.usb_to_open():
            time.sleep(5)
            result = sd.usb_to_port_a()
            time.sleep(5)
            if result:
                write_log(lib_constants.LOG_INFO, 'usb to host action is successful')
                return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'usb to host action is failed')
    return False


def usb_to_sut(soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while retry > 0:
        if sd.usb_to_open():
            time.sleep(5)
            result = sd.usb_to_port_b()
            time.sleep(5)
            if result:
                write_log(lib_constants.LOG_INFO, 'usb to sut action is successful')
                return True
        retry -= 1
    write_log(lib_constants.LOG_ERROR, 'usb to sut action is failed')
    return False


def get_jumper_switch_state(port, soundwave_port='COM101'):
    sd = get_soundwave_instance(soundwave_port)
    result = sd.get_fp_switch_state(port)
    if result is not None:
        return result
    else:
        write_log(lib_constants.LOG_ERROR, 'unable to read current port {} status'.format(port))
        return False


def set_jumper_two_ways_switch_state(port, value=1, soundwave_port='COM101', retry=3):
    sd = get_soundwave_instance(soundwave_port)
    while True:
        if retry < 0:
            write_log(lib_constants.LOG_ERROR, 'failed to set port {} jumper state to {}'.format(port, value))
            return False
        jumper_status = sd.get_fp_switch_state(port)
        if jumper_status is not None and int(jumper_status) == value:
            write_log(lib_constants.LOG_INFO, 'success to set port {} jumper state to {}'.format(port, value))
            return True
        else:
            sd.ctr_fp_two_ways_switch(port, value)
            time.sleep(3)
        retry -= 1


def get_power_status(soundwave_port='COM101', soundwave_instance=None):
    mini_voltage = 0.6
    max_voltage = 3.0
    if soundwave_instance is None:
        sd = get_soundwave_instance(soundwave_port)
    else:
        sd = soundwave_instance
    result = sd.get_ad_values([2, 11])
    main_pw = round(result[0], 5)
    p3v3_pw = round(result[1], 5)
    if main_pw <= mini_voltage and p3v3_pw <= mini_voltage:
        return 'G3'
    elif main_pw <= mini_voltage and p3v3_pw >= max_voltage:
        return 'S5'
    elif main_pw >= max_voltage and p3v3_pw >= max_voltage:
        return 'S0'
    else:
        return 'NA'


if __name__ == '__main__':
    # usb_to_host()
    # usb_to_sut()
    # ac_off()
    # ac_on()
    # print(get_jumper_switch_state(6))
    # print(set_jumper_two_ways_switch_state(6, 1))
    print(get_power_status())

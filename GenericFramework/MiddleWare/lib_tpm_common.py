import subprocess
import os
import threading
import time
import sys

import vt100_screen_parser
from lib_bios_config import BiosMenuConfig
import hal_serial_opt as hso
import library
import lib_constants
import lib_power_action_soundwave
import codecs
import lib_flash_server
import ssh
import utils
import sal_remote_fetch
import sal_pstools

IS_CASE_PASS = {"status": True}
enter_bios_timeout = 1200
reset_bios_timeout = 600
STEP_NO = 1
F2_TIMEOUT = 15
BMC_USER_NAME = ''
BMC_PWD = ''


# print the step log and result
def result_process(result, step_string, test_exit=True, is_step_complete=False):
    global STEP_NO
    if not result:
        global IS_CASE_PASS
        IS_CASE_PASS = False
        if is_step_complete:
            library.write_log(lib_constants.LOG_FAIL,
                              "\n###############################################################"
                              "############\nStep %d: Fail to %s\n###########################"
                              "###############################################"
                              "#" % (STEP_NO, step_string))
            STEP_NO += 1
        else:
            library.write_log(lib_constants.LOG_FAIL, "Failed to %s" % step_string)
        if test_exit:
            sys.exit(lib_constants.EXIT_FAILURE)
    else:
        if is_step_complete:
            library.write_log(lib_constants.LOG_INFO,
                              "\n###############################################################"
                              "############\nStep %d: Succeed to %s\n###########################"
                              "###############################################"
                              "#" % (STEP_NO, step_string))
            STEP_NO += 1
        else:
            library.write_log(lib_constants.LOG_INFO, "Succeed to %s" % step_string)


def save_serial_trace(trace_name):
    hs = hso.SerialComm()
    hs._imp_port_mngr("open")
    time_out = enter_bios_timeout
    try:
        library.write_log(lib_constants.LOG_INFO, 'starting capture serial trace')
        fp = open(trace_name, 'wb')
        while True:
            if time_out < 0:
                library.write_log(lib_constants.LOG_WARNING, 'failed to capture F2 key')
                break
            serial_log = hs._imp_buffer_sync()
            fp.write(serial_log)
            if '[F2]' in serial_log.decode('ISO-8859-1', errors='ingore'):
                library.write_log(lib_constants.LOG_INFO, 'stop capture serial trace as system boot to edk menu')
                break
            time.sleep(2)
            time_out -= 2
        fp.close()
    except Exception as e:
        library.write_log(lib_constants.LOG_WARNING, 'failed to save serial log: {}'.format(e))
    library.write_log(lib_constants.LOG_INFO, 'success capture serial trace as system boot to edk menu')


class SerialTrace(object):
    def __init__(self, path, name):
        self.capture_tag = True
        self.thread = None
        self.path = path
        self.name = name

    def save_global_serial_trace(self):
        trace_name = os.path.join(self.path,
                                  self.name + '_serial_trace_' + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + '.txt')
        trace = os.path.join(os.path.dirname(os.path.realpath(__file__)), trace_name)
        try:
            hs = hso.SerialComm()
            hs._imp_port_mngr("open")
            library.write_log(lib_constants.LOG_INFO, 'starting capture serial trace')
            self.fp = open(trace, 'wb')
            while self.capture_tag:
                serial_log = hs._imp_buffer_sync()
                self.fp.write(serial_log)
                time.sleep(2)
            self.fp.close()
        except Exception as e:
            library.write_log(lib_constants.LOG_WARNING, 'failed to save serial log: {}'.format(e))
        library.write_log(lib_constants.LOG_INFO, 'stop capture serial trace')

    def start_capture_trace(self):
        self.thread = threading.Thread(target=self.save_global_serial_trace)
        self.thread.setDaemon(True)
        self.thread.start()

    def __del__(self):
        if hasattr(self, 'fp'):
            self.fp.close()


class Step(object):
    def __init__(self, TEST_CASE_ID, SCRIPT_ID):
        self.TEST_CASE_ID = TEST_CASE_ID
        self.SCRIPT_ID = SCRIPT_ID
        # Soundwave param
        self.soundwave_port = utils.ReadConfig('SOUNDWAVE', 'PORT')
        self.jumper_port = utils.ReadConfig('SOUNDWAVE', 'JUMPER_PORT')

        # ifwi, bmc and cpld image path
        self.ifwi = utils.ReadConfig('IFWI_IMAGES', 'RELEASE')
        self.release_pfr = utils.ReadConfig('IFWI_IMAGES', 'PFR')
        self.sut_ip = utils.ReadConfig('SUT_IP', 'IP')
        if 'FAIL' in self.sut_ip and 'FAIL' in self.ifwi and 'FAIL' in self.release_pfr:
            result_process(False, 'get sut_ip ifwi release_pfr_container')

        self.bmc = utils.ReadConfig('BMC_IMAGES', 'RELEASE')
        self.cr_dimm_number = utils.ReadConfig('CR_DIMM', 'CR_DIMM_NUM')
        self.cpld = utils.ReadConfig('CPLD_IMAGES', 'RELEASE')
        if 'FAIL' in self.bmc and 'FAIL' in self.cpld and 'FAIL' in self.soundwave_port and 'FAIL' \
                in self.cr_dimm_number:
            result_process(False, 'get bmc cpld soundwave_port')

        self.remove_dimm_socket_id = utils.ReadConfig('ddr4_dimm', 'remove_dimm_socket_id')
        self.remove_dimm_channel_id = utils.ReadConfig('ddr4_dimm', 'remove_dimm_channel_id')
        if 'FAIL' in self.remove_dimm_socket_id and 'FAIL' in self.remove_dimm_channel_id:
            result_process(False, 'get bmc cpld soundwave_port')

        # USB Drive
        self.usb_alias = utils.ReadConfig('USB Drive', 'EFI_ALIAS')
        self.drive_letter = utils.ReadConfig('USB Drive', 'DRIVE_LETTER')
        if 'FAIL' in self.usb_alias and 'FAIL' in self.drive_letter:
            result_process(False, 'get USB Info')

        # tpm tool
        self.TPM_TOOL_FOLDER = utils.ReadConfig('TPM_TOOLS', 'PM_TOOL_FOLDER')
        self.pcr_dump = utils.ReadConfig('TPM_TOOLS', 'PCR_DUMP')
        self.tpm_event_dump = utils.ReadConfig('TPM_TOOLS', 'TPM_EVENT_DUMP')
        self.txt_info = utils.ReadConfig('TPM_TOOLS', 'TXT_INFO')
        if 'FAIL' in self.TPM_TOOL_FOLDER and 'FAIL' in self.pcr_dump and 'FAIL' in self.tpm_event_dump \
                and 'FAIL' in self.txt_info:
            result_process(False, 'get TPM_TOOLS')
        # ota tool
        self.OTA_TOOL_FOLDER = utils.ReadConfig('OTA_TOOLS', 'OTA_TOOL_FOLDER')
        self.OTA_App = utils.ReadConfig('OTA_TOOLS', 'OTA_App')
        if 'FAIL' in self.OTA_TOOL_FOLDER and 'FAIL' in self.OTA_App:
            result_process(False, 'get OTA_TOOLS')

        # tpm_provision
        self.TPM_PROV_FOLDER = utils.ReadConfig('TPM_Provision', 'TPM_PROV_FOLDER')
        self.RSTPLATAUTH = utils.ReadConfig('TPM_Provision', 'RSTPLATAUTH')
        self.TPM2TXTPROV = utils.ReadConfig('TPM_Provision', 'TPM2TXTPROV')
        self.TPM2POPROV = utils.ReadConfig('TPM_Provision', 'TPM2POPROV')
        self.TPM2SGXIPROV = utils.ReadConfig('TPM_Provision', 'TPM2SGXIPROV')
        self.TPM_CHANGEEPS = utils.ReadConfig('TPM_Provision', 'TPM_CHANGEEPS')
        if 'FAIL' in self.TPM_PROV_FOLDER and 'FAIL' in self.RSTPLATAUTH and 'FAIL' in self.TPM2TXTPROV \
                and 'FAIL' in self.TPM2POPROV and 'FAIL' in self.TPM2SGXIPROV:
            result_process(False, 'get TPM_PROV_TOOLS')

        # SECURE_BOOT_KEYS
        self.KEYS_FOLDER = utils.ReadConfig('SECURE_BOOT_KEYS', 'KEYS_FOLDER')
        self.KEK_CER = utils.ReadConfig('SECURE_BOOT_KEYS', 'KEK_CER')
        self.PROP_CER = utils.ReadConfig('SECURE_BOOT_KEYS', 'PROP_CER')
        self.UEF_CER = utils.ReadConfig('SECURE_BOOT_KEYS', 'UEF_CER')
        self.PK_CER = utils.ReadConfig('SECURE_BOOT_KEYS', 'PK_CER')
        self.GUID = utils.ReadConfig('SECURE_BOOT_KEYS', 'GUID')
        if 'FAIL' in self.KEYS_FOLDER and 'FAIL' in self.KEK_CER and 'FAIL' in self.PROP_CER \
                and 'FAIL' in self.UEF_CER and 'FAIL' in self.PK_CER and 'FAIL' in self.GUID:
            result_process(False, 'get SECURE_BOOT_KEYS')

        # windows
        self.WD_HD_SERIAL = utils.ReadConfig('WINDOWS', 'HD_SERIAL')
        self.WD_USERNAME = utils.ReadConfig('WINDOWS', 'USERNAME')
        self.WD_PASSWORD = utils.ReadConfig('WINDOWS', 'PASSWORD')
        if 'FAIL' in self.WD_HD_SERIAL and 'FAIL' in self.WD_USERNAME and 'FAIL' in self.WD_PASSWORD:
            result_process(False, 'get Windows')

        # Quartus param
        self.quartus_pgm_binary = utils.ReadConfig('Quartus', 'quartus_pgm_binary')
        self.jtag_binary = utils.ReadConfig('Quartus', 'jtag_binary')
        self.expect_cables = utils.ReadConfig('Quartus', 'expect_cables')
        self.regex_device = utils.ReadConfig('Quartus', 'regex_device')
        self.system_console_bin = utils.ReadConfig('Quartus', 'system_console_bin')

        # REDHAT
        self.LN_HD_SERIAL = utils.ReadConfig('REDHAT', 'HD_SERIAL')
        self.LN_USERNAME = utils.ReadConfig('REDHAT', 'USERNAME')
        self.LN_PASSWORD = utils.ReadConfig('REDHAT', 'PASSWORD')
        if 'FAIL' in self.LN_HD_SERIAL and 'FAIL' in self.LN_HD_SERIAL and 'FAIL' in self.LN_HD_SERIAL:
            result_process(False, 'get Redhat')

        # OOB_Host
        self.PLINK_PATH = utils.ReadConfig('OOB_Host', 'PLINK_PATH')
        self.OOB_HOST_USER = utils.ReadConfig('OOB_Host', 'OOB_HOST_USER')
        self.OOB_HOST_PWD = utils.ReadConfig('OOB_Host', 'OOB_HOST_PWD')
        self.OOB_HOST_IP = utils.ReadConfig('OOB_Host', 'OOB_HOST_IP')
        if 'FAIL' in self.PLINK_PATH and 'FAIL' in self.OOB_HOST_USER and 'FAIL' in self.OOB_HOST_PWD \
                and 'FAIL' in self.OOB_HOST_IP:
            result_process(False, 'get OOB_Host')

        self.bios_conf = BiosMenuConfig(TEST_CASE_ID, SCRIPT_ID)

    def run(self):
        try:
            self.case_step()
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, str(e), self.TEST_CASE_ID, self.SCRIPT_ID)
            result_process(False, str(e))
            self.tear_down()
        finally:
            self.tear_down()

    def case_step(self):
        pass

    def tear_down(self, windows=False, redhat=False):
        if self.device_in_os() and windows == True:
            result_process(True, 'Detect SUT in OS.')
            shutdown_sut = self.plink_wmi_run_remote_cmd('shutdown -s -t 5')
            if not shutdown_sut:
                dc_off = lib_power_action_soundwave.dc_off()
                result_process(dc_off, step_string='Perform DC OFF',
                               test_exit=False)
            time.sleep(30)
        ac_off = lib_power_action_soundwave.ac_off()
        result_process(ac_off, step_string='Perform AC OFF', test_exit=False)

    def init_config(self):
        pass

    def flash_bios_boot_setup(self):
        result = False
        usb_to_sut = lib_power_action_soundwave.usb_to_sut()
        time.sleep(5)
        result_process(usb_to_sut, 'USB to SUT')

        flash_result = lib_flash_server.flashifwi_em100(self.ifwi)
        result_process(flash_result, "Flash BIOS")
        ac_on = lib_power_action_soundwave.ac_on()
        result_process(ac_on, "Power on after flashi)ng BIOS")
        result = self.bios_conf.enter_bios(f2_timeout=F2_TIMEOUT)
        return result

    def enter_edk_shell(self):
        result = self.bios_conf.bios_back_home()
        result_process(result, 'Back to home page')
        usb_to_sut = lib_power_action_soundwave.usb_to_sut()
        result_process(usb_to_sut, 'USB to SUT')
        time.sleep(5)
        efi_alias = self.bios_conf.enter_efi_shell(volume_alias=self.usb_alias, time_out=30, bios_navi_time=5)
        result = efi_alias and len(efi_alias) > 0
        self.bios_conf.efi_shell_cmd(efi_alias)
        return result

    def set_debug_level(self):
        step_string = "Set serial debug message level to 'Normal'"
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Platform Configuration", "Miscellaneous Configuration"])
        result_process(result, step_string)
        result = self.bios_conf.bios_opt_drop_down_menu_select("Serial Debug Message Level", "Normal")
        result = result and self.bios_conf.bios_save_changes()
        return result

    def reboot_get_log(self, filname):
        step_string = "Collect the serial log after reboot the device."
        result = self.bios_conf.bios_back_home()
        result_process(result, 'back to home page')
        hs = hso.SerialComm()
        hs._imp_port_mngr("open")  # begin capture serial log
        result = self.bios_conf.bios_initialize(f2_press_wait=20)
        # result = self.bios_conf.reset_to_bios()
        serial_log = hs._imp_buffer_sync()
        print(type(serial_log), len(serial_log))
        # stop capture serial log
        result = result and serial_log is not None
        result_process(result, step_string, is_step_complete=True)
        output_log = vt100_screen_parser.parse_edk_shell(serial_log)
        print(type(output_log), len(output_log))
        time.sleep(10)
        with open(filname, 'w') as f:
            f.write(output_log)
            time.sleep(10)
        return output_log

    def enable_secure_boot(self, value=True):
        if value:
            self.bios_conf.bios_back_home()
            result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Secure Boot Configuration'])
            result_process(result, 'Enter EDKII Menu-> Secure Boot Configuration')
            result = self.bios_conf.bios_opt_drop_down_menu_select('Secure Boot Mode', 'Custom Mode')
            result_process(result, 'Set Secure Boot Mode = Custom Mode')
            result = self.bios_conf.bios_menu_navi(['Custom Secure Boot Options'])
            result_process(result, 'Enter Custom Secure Boot Option')

            # set KEK
            result = self.bios_conf.bios_menu_navi(['KEK Options', 'Enroll KEK', 'Enroll KEK using File'])
            result_process(result, 'Enter USB File Explorer')
            usb_volume_name = 'USB'
            kek_file_path = self.KEYS_FOLDER + '/' + self.KEK_CER
            result = self.bios_conf.bios_file_explorer(usb_volume_name, kek_file_path, wait_time=15)
            result_process(result, 'Select kek file')
            result = self.bios_conf.bios_opt_dialog_box_input('Signature GUID', self.GUID)
            result_process(result, 'Set signature GUID')
            result = self.bios_conf.bios_menu_navi(['Commit Changes and Exit'])
            result_process(result, 'Save Change')

            # set DB_1
            result = self.bios_conf.bios_menu_navi(['DB Options', 'Enroll Signature', 'Enroll Signature Using File'])
            result_process(result, 'Enter USB File Explorer')
            db_file_1_path = self.KEYS_FOLDER + '/' + self.PROP_CER
            db_file_2_path = self.KEYS_FOLDER + '/' + self.UEF_CER
            result = self.bios_conf.bios_file_explorer(usb_volume_name, db_file_1_path, wait_time=15)
            result_process(result, 'Select DB file 1')
            result = self.bios_conf.bios_opt_dialog_box_input('Signature GUID', self.GUID)
            result_process(result, 'Set signature GUID')
            result = self.bios_conf.bios_menu_navi(['Commit Changes and Exit'])
            result_process(result, 'Save Change')

            # set DB_2
            result = self.bios_conf.bios_menu_navi(['DB Options', 'Enroll Signature', 'Enroll Signature Using File'])
            result_process(result, 'Enter USB File Explorer')
            result = self.bios_conf.bios_file_explorer(usb_volume_name, db_file_2_path, wait_time=15)
            result_process(result, 'Select DB file 2')
            result = self.bios_conf.bios_opt_dialog_box_input('Signature GUID', self.GUID)
            result_process(result, 'Set signature GUID')
            result = self.bios_conf.bios_menu_navi(['Commit Changes and Exit'])
            result_process(result, 'Save Change')

            # set PK
            result = self.bios_conf.bios_menu_navi(['PK Options', 'Enroll PK', 'Enroll PK Using File'])
            result_process(result, 'Enter USB File Explorer')
            pk_file_path = self.KEYS_FOLDER + '/' + self.PK_CER
            result = self.bios_conf.bios_file_explorer(usb_volume_name, pk_file_path, wait_time=15)
            result_process(result, 'Select PK file')
            result = self.bios_conf.bios_menu_navi(['Commit Changes and Exit'])
            result_process(result, 'Save Change')

            self.bios_conf.bios_back_home()
            result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Secure Boot Configuration'])
            result_process(result, 'Enter EDKII Menu->Secure Boot Configuration')
            secure_boot = self.bios_conf.get_system_information('Attempt Secure Boot')
            if '[X]' in secure_boot:
                return True
            else:
                return False
        else:
            self.bios_conf.bios_back_home()
            result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Secure Boot Configuration'])
            result_process(result, 'Enter EDKII Menu-> Secure Boot Configuration')
            result = self.bios_conf.bios_opt_drop_down_menu_select('Secure Boot Mode', 'Custom Mode')
            result_process(result, 'Set Secure Boot Mode = Custom Mode')
            result = self.bios_conf.bios_menu_navi(['Custom Secure Boot Options'])
            result_process(result, 'Enter Custom Secure Boot Option')

            # set PK
            self.bios_conf.bios_menu_navi(['PK Options', 'Delete Pk'])
            result = self.bios_conf.bios_save_changes()
            result_process(result, 'Disable secueboot')
            return result

    def device_in_os(self):
        cmd = "ping {0}".format(self.sut_ip)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        if b'destination host unreachable' in output or b'could not find' in output \
                or b'Request timed out' in output:
            return False
        else:
            return True

    def reboot_to_windows(self):
        result = self.bios_conf.bios_back_home()
        Windows_HD = self.WD_HD_SERIAL
        result_process(result, 'Back to home page.')
        result = self.bios_conf.reset_system()
        result_process(result, 'Reset system in BIOS.')
        setup_result = self.bios_conf.select_boot_device(device_name=Windows_HD, f7_timeout=20)
        result_process(setup_result, 'Select windows as boot device')
        time.sleep(420)
        # result = self.device_in_os()
        return setup_result

    def plink_wmi_run_remote_cmd(self, cmd, time_out=60, response = True):
        ssh_cmd = "echo y | {0} -ssh {1}@{2} -pw {3} {4}".format(self.PLINK_PATH, self.WD_USERNAME, self.sut_ip,
                                                                 self.WD_PASSWORD, cmd)
        process = subprocess.Popen(ssh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(ssh_cmd)
        output = process.communicate(timeout=time_out)[0]
        error = process.communicate(timeout=time_out)[1]
        output = str(output, encoding='utf-8', errors='ignore')
        if response:
            return output

    def wmi_run_remote_cmd(self, cmd, text_exit=True):
        usb_letter = self.drive_letter
        remote_log = 'tpm_status.txt'
        remote_log_path = os.path.join(usb_letter, remote_log)
        local_cmd_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), r'tpm_opt.cmd')
        remote_cmd_file = os.path.join(usb_letter, r'tpm_opt.cmd')
        with open(local_cmd_file, 'w') as f:
            cmd_line = "{0} > {1} ".format(cmd, remote_log_path)
            f.write(cmd_line)
            f.close()
        put_file = sal_remote_fetch.remote_put(local_cmd_file, remote_cmd_file)
        result_process(put_file, 'Put cmd file to SUT.', test_exit=text_exit)
        ps_ret = sal_pstools.ps_tools_run(remote_cmd_file, remo_file=True)
        result_process(ps_ret, 'Run remote cmd: {0}.'.format(cmd),
                       test_exit=text_exit)
        return ps_ret

    def check_manage_bde_log(self, line, expected_value, expect_key='Conversion Status'):
        if line == '':
            return False
        lines = line.strip().split('\r\n')
        volume_c_key = 'Volume C: []'
        volume_c_index = lines.index(volume_c_key)
        result = False
        for i in range(volume_c_index, len(lines)):
            if expect_key in lines[i]:
                result = expected_value in lines[i]
                break
        return result

    def set_tpm_operation(self, value):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu",
                                           "TCG2 Configuration"])
        result_process(result, 'Enter EDKII Menu->TCG2 Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select('TPM2 Operation', value)
        result_process(result, 'Set TPM Operation:{0}'.format(value))
        self.bios_conf.bios_save_changes()
        return result

    def reset_with_menu(self):
        self.bios_conf.bios_back_home()
        reboot = self.bios_conf.bios_menu_navi(['Reset'])
        result_process(reboot, 'Reset the system')
        return reboot

    def pcr_bank_opt(self, sha1_check=None, sha256_check=None):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'TCG2 Configuration'])
        result_process(result, 'Enter EDKII Menu->TCG2 Configuration')
        result_sha1 = result_sha256 = True
        if sha1_check is not None:
            result_sha1 = self.bios_conf.bios_opt_checkbox_check('PCR Bank: SHA1', sha1_check)
        if sha256_check is not None:
            result_sha256 = self.bios_conf.bios_opt_checkbox_check('PCR Bank: SHA256', sha256_check)
        self.bios_conf.bios_save_changes()
        return result_sha1 and result_sha256

    def decrypted_c(self):
        cmd = 'manage-bde -status'
        status = self.plink_wmi_run_remote_cmd(cmd)
        result_decryted = self.check_manage_bde_log(status, 'Fully Decrypted')
        if not result_decryted:
            cmd = 'manage-bde -off C:'
            self.plink_wmi_run_remote_cmd(cmd)
        while not result_decryted:
            time.sleep(60)
            cmd = 'manage-bde -status'
            status = self.plink_wmi_run_remote_cmd(cmd)
            result_decryted = self.check_manage_bde_log(status, 'Fully Decrypted')
            result_process(True, 'Get current decrpytion process:\n{0}'.format(status))
        result_process(result_decryted, 'fully Decrypted')

    def check_pcr_bank(self):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "TCG2 Configuration"])
        result_process(result, 'Enter EDKII Menu/TCG2 Configuration')
        self.bios_conf.select_menu_option('PCR Bank: SHA1')
        is_sha1_checked = self.bios_conf.is_checkbox_checked()
        self.bios_conf.select_menu_option('PCR Bank: SHA256')
        is_sha256_checked = self.bios_conf.is_checkbox_checked()
        result = is_sha1_checked and is_sha256_checked
        return result

    # flash cpld
    def flash_cpld_image(self):
        # step Pre requisite flash CPLD
        cpld = self.cpld
        soundwave_port = self.soundwave_port
        quartus_pgm_binary = self.quartus_pgm_binary
        jtag_binary = self.jtag_binary
        expect_cables = self.expect_cables
        regex_device = self.regex_device
        if not lib_flash_server.flash_cpld(cpld, soundwave_port=soundwave_port, binary=quartus_pgm_binary,
                                           jtag_binary=jtag_binary, expect_cables=expect_cables,
                                           regex_device=regex_device):
            result_process(False, 'Flash CPLD')
        else:
            result_process(True, 'Flash CPLD')

    def provision_tpm(self):
        self.enter_edk_shell()
        cmd_reset = self.RSTPLATAUTH
        cmd_txt = self.TPM2TXTPROV
        cmd_po = self.TPM_PROV_FOLDER
        cmd_sgxi = self.TPM2SGXIPROV
        TPMPROV_FOLDER = self.TPM_PROV_FOLDER
        cmd = "cd {0}".format(TPMPROV_FOLDER)
        self.bios_conf.efi_shell_cmd(cmd)
        expect_log = "Successfully set PlatformAuth to EMPTY"
        cmd_reset += ' sha256 example'
        serial_log = self.bios_conf.efi_shell_cmd(cmd_reset, time_out=30)
        result1 = expect_log in serial_log
        expect_log = "Provisioning Completed Successfully"
        cmd_txt += ' SHA256 EXAMPLE'
        serial_log = self.bios_conf.efi_shell_cmd(cmd_txt, time_out=30)
        result2 = expect_log in serial_log
        cmd_po += ' SHA256 EXAMPLE'
        serial_log = self.bios_conf.efi_shell_cmd(cmd_po, time_out=30)
        result3 = expect_log in serial_log
        cmd_sgxi += ' SHA256 EXAMPLE'
        serial_log = self.bios_conf.efi_shell_cmd(cmd_sgxi,time_out=30)
        result4 = expect_log in serial_log
        return result1 and result2 and result3 and result4

    def enable_processor_config(self):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration",
                                                "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->"
                               "Processor Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("VMX", "Enable")
        result_process(result, "Enable VMX")
        result = self.bios_conf.bios_opt_drop_down_menu_select("MSR Lock Control",
                                                               "Enable")
        result_process(result, "Enable MSR Lock Control")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Enable SMX",
                                                               "Enable")
        result_process(result, "Enable SMX")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Enable Intel(R) TXT",
                                                               "Enable")
        result_process(result, "Enable Intel(R) TXT")
        self.bios_conf.bios_save_changes()

    def vt_d_opt(self, value='Enable'):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "IIO Configuration",
                                                "VT for Directed I/O (VT-d)"], complete_matching=False)
        result_process(result, 'Enter EDKII Menu->Socket Configuration->IIO '
                               'Configuration->Intel VT for Directed I/O (VT-d)')
        vd_d_menu = "VT for Directed I/O (VT-d)"
        result = self.bios_conf.bios_opt_drop_down_menu_select("VT for Directed I/O (VT-d)", value,
                                                               complete_matching=False)
        self.bios_conf.bios_save_changes()
        result_process(result, "Set VT for Directed I/O(VT-d)={0}".format(value), is_step_complete=True)

    def dump_pcr_info(self, pcr_log, event_log, txt_info):

        cmd = "cd {0}".format(self.TPM_TOOL_FOLDER)
        self.bios_conf.efi_shell_cmd(cmd)
        cmd = "{0} -v > {1}".format(self.pcr_dump, pcr_log)
        self.bios_conf.efi_shell_cmd(cmd)
        if event_log:
            cmd = "{0} > {1}".format(self.tpm_event_dump, event_log)
            self.bios_conf.efi_shell_cmd(cmd)
        if txt_info:
            cmd = "{0} -c a -a > {1}".format(self.txt_info, txt_info)
            self.bios_conf.efi_shell_cmd(cmd)

    @staticmethod
    def compare_pcr0to7_fromfile(filename1, filename2):
        pcr_value_2 = []
        with open(filename1, encoding='utf-16') as f:
            lines = f.readlines()
            index = 0
            for line in lines:
                key = "TPM PCR {0}:".format(index)
                if key in line:
                    pcr_value_2.append(line.strip())
                    index += 1
                if index > 7:
                    break

        result_process(False, "Found file {0}".format(pcr_value_2), test_exit=False)

        with open(filename2, encoding='utf-16') as f:
            lines = f.readlines()
            pcr_value_4 = []
            index = 0
            for line in lines:
                key = "TPM PCR {0}:".format(index)
                if key in line:
                    pcr_value_4.append(line.strip())
                    index += 1
                if index > 7:
                    break
        result_process(False, "Found file: {0}".format(pcr_value_4), test_exit=False)

        if len(pcr_value_2) != 8 and len(pcr_value_4) != 8:
            result_process(False, 'Get pcr value from step3 and step5', test_exit=False, is_step_complete=True)
        else:
            result = pcr_value_2[0].replace(' ', '') != pcr_value_4[0].replace(' ', '')
            result = result and pcr_value_2[7].replace(' ', '') != pcr_value_4[7].replace(' ', '')
            result1_5 = True
            for i in range(1, 7):
                result1_5 = result1_5 and pcr_value_2[i].replace(' ', '') == pcr_value_4[i].replace(' ', '')
            result = result1_5 and result
            return result

    @staticmethod
    def check_tpm_event(tpm_event_log, check_pcr=False, dma_log_exist=True):
        if os.path.exists(tpm_event_log):
            # compare eva value and pcr value
            if check_pcr:
                eval_value_00 = None
                pcr_value_00 = None
                with open(tpm_event_log, encoding='utf-16') as f:
                    lines = f.readlines()
                    for index, line in enumerate(lines):
                        if "Check SHA256 EventLog and TPM SHA256 PCR" in line:
                            eval_value_00 = lines[index + 2].strip() + lines[index + 3].strip()
                            pcr_value_00 = lines[index + 5].strip() + lines[index + 6].strip()
                            break
                step_string = "\nEVAL_VALUE[00]: {0}\nPCR_VALUE[00]: {1}".format(eval_value_00, pcr_value_00)
                is_value_same = False
                if eval_value_00 is not None and pcr_value_00 is not None:
                    eval_value_00 = eval_value_00.replace(' ', '')
                    pcr_value_00 = pcr_value_00.replace(' ', '')
                    is_value_same = eval_value_00.lower() == pcr_value_00.lower()
                result_process(is_value_same, step_string, test_exit=False)

            # check dma_protection_disabled log
            dma_log = 'DMA Protection'
            with open(tpm_event_log, encoding='utf-16') as f:
                if dma_log_exist:
                    dma_ret = dma_log in f.read()
                    result_process(dma_ret, "Found '{0}' in event log.".format(dma_log), is_step_complete=True)
                else:
                    dma_ret = dma_log not in f.read()
                    result_process(dma_ret, "'{0}' should not in event log.".format(dma_log), is_step_complete=True)

    @staticmethod
    def wait_and_press_f12(time_out=600):
        hs = hso.SerialComm()
        hs._imp_port_mngr("open")  # begin capture serial log
        key_word = b'Press F12'
        wait_time = time_out
        found_f12 = False
        while wait_time:
            time.sleep(2)
            serial_log = hs._imp_buffer_sync()  # stop capture serial log
            found_f12 = key_word in serial_log
            if found_f12:
                break
            wait_time -= 2
        result_process(found_f12, "Found 'Press F12' in serial log")
        if found_f12:
            hs.serial_io_hii_enum(2, 'F12', key_step=5)
        return found_f12

    def set_tcg2_configuration(self, option, attempt_rev):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'TCG2 Configuration'])
        result_process(result, 'Enter EDKII Menu->TCG2 Configuration')
        self.bios_conf.bios_opt_drop_down_menu_select(option, attempt_rev)
        result_process(result,'Set option{0}'.format(attempt_rev))
        self.bios_conf.bios_save_changes()

    def check_tcg2_configuration(self, option, current_rev):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'TCG2 Configuration'])
        result_process(result, 'Enter EDKII Menu->TCG2 Configuration')
        cur_rev = self.bios_conf.get_system_information(option)
        result = cur_rev == current_rev
        return result

    def check_tpm_device(self):
        tpm_device = self.bios_conf.get_system_information('Current TPM Device')
        result_device = tpm_device == 'TPM 2.0'
        tpm_interface = self.bios_conf.get_system_information('Current TPM Device Interface')
        result_interface = 'TIS' == tpm_interface or 'PTP FIFO' == tpm_interface
        return result_device and result_interface

    @staticmethod
    def verify_expectlog_infile(expect_log, filename):
        result = False
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                if expect_log in line:
                    result = True
                    break
        return result

    def check_log(self, expect_log_dic):
        # check log
        remote_log = 'tpm_status.txt'
        local_log_path = os.path.join(self.drive_letter, remote_log)
        with open(local_log_path) as f:
            logs = f.readlines()
        check_log_result = False
        find_log = ""
        for key in expect_log_dic.keys():
            for log in logs:
                if key.lower() in log.lower():
                    check_log_result = expect_log_dic[key].lower() in log.lower()
                    find_log = log
                    break
        result_process(check_log_result, 'Check log, expected log is: {0}; actural log is: {1}'.format(
            str(expect_log_dic), find_log))
        return check_log_result

    def get_eval_pcr(self, tpm_event_log):
        tpm_event = os.path.join(self.drive_letter, self.TPM_TOOL_FOLDER, tpm_event_log)
        if os.path.exists(tpm_event):
            with open(tpm_event, encoding='utf-16') as f:
                lines = f.readlines()
                title_index = None
                for index, line in enumerate(lines):
                    if "Check SHA256 EventLog and TPM SHA256 PCR" in line:
                        title_index = index
                        break
                if title_index is not None:
                    for index in range(title_index, len(lines)):
                        if "EVA_VALUE[02]" in lines[index]:
                            eval_value_02 = lines[index + 1].strip() + lines[index + 2].strip()
                            break
            step_string = "\nEVAL_VALUE[02]: {0}".format(eval_value_02)
            result = eval_value_02 is not None
            result_process(result, step_string)
        else:
            result_process(False, "Found file: {0}".format(tpm_event))
        return eval_value_02

    def compare_pcr2_value(self, eval_pcr_02, PCRDUMP_LOG):
        usb_to_host = lib_power_action_soundwave.usb_to_host()
        result_process(usb_to_host, "USB To Host")
        time.sleep(5)

        pcr_dump_log = os.path.join(self.drive_letter, self.TPM_TOOL_FOLDER, PCRDUMP_LOG)
        if os.path.exists(pcr_dump_log):
            actual_pcr_02 = None
            with open(pcr_dump_log, encoding='utf-16') as f:
                lines = f.readlines()
                for line in lines:
                    if "TPM PCR 2:" in line:
                        actual_pcr_02 = line
            if actual_pcr_02 is not None:
                actual_pcr_02 = actual_pcr_02.replace("TPM PCR 2:", "").strip()
                actual_pcr_02 = actual_pcr_02.replace(' ', '')
            if eval_pcr_02 is not None and actual_pcr_02 is not None:
                eval_pcr_02 = eval_pcr_02.replace(' ', '')
                result = actual_pcr_02.lower() == eval_pcr_02.lower()
                return result

    def repeat_step3_to_7(self, pcr_log, event_Log):
        result = self.enter_edk_shell()
        cmd = "cd {0}".format(self.TPM_TOOL_FOLDER)
        self.bios_conf.efi_shell_cmd(cmd)
        cmd = "{0} -v > {1}".format(self.pcr_dump, pcr_log)
        self.bios_conf.efi_shell_cmd(cmd)
        cmd = "{0} > {1}".format(self.tpm_event_dump, event_Log)
        self.bios_conf.efi_shell_cmd(cmd)
        result = result and self.check_event_type(": check Event_type", 'EventType : [800000E1]')
        result_process(result, ": check Event_type")
        eval_pcr_02 = self.get_eval_pcr(": get EVA_PCR_02")
        result = result and eval_pcr_02 is not None
        compare_ret = self.compare_pcr2_value(': compare PCR02 value', eval_pcr_02)
        result = result and compare_ret
        return result

    def check_event_type(self, expected_log, TPM_EVENT_LOG):
        usb_to_host = lib_power_action_soundwave.usb_to_host()
        result_process(usb_to_host, 'USB to Host')
        time.sleep(5)
        result = False
        event_num = 2 * int(self.cr_dimm_number)
        tpm_event_path = os.path.join(self.drive_letter, self.TPM_TOOL_FOLDER, TPM_EVENT_LOG)
        event_count = 0
        print(tpm_event_path)
        with open(tpm_event_path, encoding='utf-16') as f:
            lines = f.readlines()
            for line in lines:
                if expected_log in line:
                    event_count += 1
        print(event_count)
        print(event_num)
        result = event_count == event_num
        return result

    @staticmethod
    def compare_pcr_value(step_string, pre_pcr_value, cur_pcr_value):
        if len(pre_pcr_value) == len(cur_pcr_value) and len(
                cur_pcr_value) is not 0 and len(pre_pcr_value) is not 0:
            result = True
            for i in range(len(pre_pcr_value)):
                pre_pcr = pre_pcr_value[i].replace(' ', '')
                cur_pcr = cur_pcr_value[i].replace(' ', '')
                compare_ret = pre_pcr == cur_pcr
                result = result and compare_ret
                if not compare_ret:
                    step_string += '\nprevious pcr: {0}\ncurrent pcr: ' \
                                   '{1}'.format(pre_pcr_value[i], cur_pcr_value[i])
                    result_process(result, step_string, test_exit=False)
        else:
            result = False
        return result

    @staticmethod
    def get_pcr_value(serial_log):
        pcr_value = []
        lines = serial_log.split('\r\n')
        for i in range(8):
            key = 'PCR {0}:'.format(i)
            for line in lines:
                if key in line:
                    pcr_value.append(line.strip())
                    break
        return pcr_value

    def run_tpm_cmd(self, efi_alias):
        self.bios_conf.efi_shell_cmd(efi_alias)
        cmd = "cd {0}".format(self.TPM_TOOL_FOLDER)
        self.bios_conf.efi_shell_cmd(cmd)
        cmd = "{0} -v".format(self.pcr_dump)
        serial_log = self.bios_conf.efi_shell_cmd(cmd, time_out=30)
        return serial_log

    def tpmevent_dump_to_file(self, efi_alias, file_name):
        self.bios_conf.efi_shell_cmd(efi_alias)
        cmd = "cd {0}".format(self.TPM_TOOL_FOLDER)
        self.bios_conf.efi_shell_cmd(cmd)
        cmd = "{0} > {1}".format(self.tpm_event_dump, file_name)
        self.bios_conf.efi_shell_cmd(cmd, time_out=30)

    def dimm_opt(self, opt='Disable'):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(
            ["EDKII Menu", "Socket Configuration", "Memory Configuration", "Memory Dfx Configuration"])
        result_process(result, 'Enter Memory Dfx Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select('DIMM Rank Enable Mask', 'Enable')
        result_process(result, 'Enable DIMM Rank Enable Mask')
        result = False
        socket_id = self.remove_dimm_socket_id
        channel_id = self.remove_dimm_channel_id
        menu = 'Socket {0} Channel {1} Rank Enable BitMask'.format(socket_id, channel_id)
        if opt.upper() == 'DISABLE':
            result = self.bios_conf.bios_opt_textbox_input(menu, '00')
        elif opt.upper() == 'ENABLE':
            result = self.bios_conf.bios_opt_textbox_input(menu, 'FF')
        result_process(result, "{0} DIMM".format(opt))
        self.bios_conf.bios_save_changes()

    def change_boot_order(self):
        result = self.bios_conf.bios_menu_navi(
            ['Boot Maintenance Manager', 'Boot Options', 'Change Boot Order'])
        result_process(result, 'Enter Boot Maintenance Manager->Boot Options')
        order_set = self.bios_conf.bios_set_boot_order('UEFI Internal Shell')
        order_set = order_set and self.bios_conf.bios_menu_navi(
            ['Commit Changes and Exit'])
        result_process(order_set, 'Set EDK Shell to first boot order.')
        self.bios_conf.bios_back_home()

    def get_shell_efi_alias(self):
        self.bios_conf.bios_back_home()
        efi_alias = ""
        if 'FAIL' in self.usb_alias:
            result_process(False, 'get usb alias from config')
        else:
            efi_alias = self.bios_conf.enter_efi_shell(volume_alias=self.usb_alias, time_out=30, bios_navi_time=5)
            result = efi_alias and len(efi_alias) > 0
            result_process(result, 'Enter EDK Shell')
        return efi_alias

    def write_log_to_file(self, serial_Log, file_name):
        f = open(file_name)
        f.write(serial_Log)
        time.sleep(10)
        f.close()

    def bios_enable_txt(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->Processor Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("VMX", "Enable")
        result_process(result, "Enable VMX")
        result = self.bios_conf.bios_opt_drop_down_menu_select("MSR Lock Control", "Enable")
        result_process(result, "Enable MSR Lock Control")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Enable SMX", "Enable")
        result_process(result, "Enable SMX")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Enable Intel(R) TXT", "Enable")
        result_process(result, "Enable Intel(R) TXT")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def bios_enable_vt_d(self):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "IIO Configuration",
                                                "VT for Directed I/O (VT-d)"], complete_matching=False)
        result_process(result,
                       'Enter EDKII Menu->Socket Configuration->IIO-Configuration->Intel VT for Directed I/O (VT-d)')
        result = self.bios_conf.bios_opt_drop_down_menu_select("Intel? VT for Directed I/O", "Enable",
                                                          complete_matching=False)
        self.bios_conf.bios_save_changes()
        return result

    def enable_tme_config(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->Processor Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Total Memory Encryption (TME)", "Enable")
        result_process(result, "Enable TME")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()
        return result

    @staticmethod
    def get_pcr_dist_fromfile(file_name, pcr=False, mktme=False):
        i = 0
        event_value = ''
        pcr_value = ''
        tme_digest = ''
        mktme_dist = ''
        tme_value = r'FeatureTME'
        mktme_value = r'FeatureMKT'
        sha256 = r'Check SHA256 EventLog and TPM SHA256 PCR'
        fp2 = codecs.open(file_name, 'r', 'utf-16')
        lines = fp2.readlines()
        fp2.close()
        for line in lines:
            i = i + 1
            if tme_value in line:
                tme_digest = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        i = 0
        for line in lines:
            i = i + 1
            if mktme_value in line:
                mktme_dist = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        i = 0
        for line in lines:
            i = i + 1
            if sha256 in line:
                event_value = lines[i + 8].strip() + ' ' + lines[i + 9].strip()
                pcr_value = lines[i + 11].strip() + ' ' + lines[i + 12].strip()
                break
        if pcr:
            dict = [event_value, pcr_value]
        elif mktme:
            dict = [tme_digest, mktme_dist, event_value, pcr_value]
        else:
            dict = [tme_digest, event_value, pcr_value]
        return dict

    def edk_shell_run_cmd(self, cmd, expect_log):
        cmd_output = self.bios_conf.efi_shell_cmd(cmd, time_out=20)
        result = expect_log.lower() in cmd_output.lower()
        return result

    def enable_mktme_config(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->"
                               "Processor Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Limit CPU PA to 46 bits", "Disable")
        result_process(result, "Disable Limit CPU PA to 46 bits")
        result = self.bios_conf.bios_opt_drop_down_menu_select('Total Memory Encryption Multi-Tenant(TME-MT)', "Enable")
        result_process(result, "Enable MK-TME")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()
        return result

    @staticmethod
    def check_pci_value(file_name):
        pcr_index = r'PCRIndex  : [00000001]'
        event_txype = r'EventType : [0000000A]'
        i = 0
        result = False
        fp2 = codecs.open(file_name, 'r', 'utf-16-le')
        lines = []
        lines = fp2.readlines()
        fp2.close()
        for line in lines:
            i = i + 1
            if pcr_index in line and event_txype in lines[i]:
                result = True
                break
        return result

    @staticmethod
    def get_msrdist_dict_fromefile(file_name):
        i = 0
        fp2 = codecs.open(file_name, 'r', 'utf-16')
        lines = fp2.readlines()
        fp2.close()
        active = 'MSR_TME_ACTIVATE'
        capability = 'MSR_TME_CAPABILI'
        exclude_base = 'MSR_TME_EXCLUDE_'
        MSR_TME_ACTIVATE = ''
        MSR_TME_CAPABILITY = ''
        MSR_TME_EXCLUDE_BASE = ''
        MSR_TME_EXCLUDE_MASK = ''
        for line in lines:
            i = i + 1
            if active in line:
                MSR_TME_ACTIVATE = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        i = 0
        for line in lines:
            i = i + 1
            if capability in line:
                MSR_TME_CAPABILITY = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        i = 0
        for line in lines:
            i = i + 1
            if exclude_base in line and 'BASE' in lines[i]:
                MSR_TME_EXCLUDE_BASE = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        i = 0
        for line in lines:
            i = i + 1
            if exclude_base in line and 'MASK' in lines[i]:
                MSR_TME_EXCLUDE_MASK = lines[i - 4].strip() + ' ' + lines[i - 3].strip()
                break
        dict = [MSR_TME_ACTIVATE, MSR_TME_CAPABILITY, MSR_TME_EXCLUDE_BASE, MSR_TME_EXCLUDE_MASK]
        return dict

    def inspect_value(self):
        result1 = self.enable_tme_config()
        result2 = self.enable_mktme_config()
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration",
                                           "Processor Configuration", "Processor Dfx Configuration"])
        result_process(result, 'Enter Processor Configuration')
        result = False
        TME_Exclusion_Base = self.bios_conf.get_system_information('TME Exclusion Base Address Increment Value')
        print('TME_Exclusion_Base is {0}'.format(TME_Exclusion_Base))
        TME_Exclusion_Length = self.bios_conf.get_system_information('TME Exclusion Length Increment value')
        # if TME_Exclusion_Base == '[0]' and TME_Exclusion_Length == '[0]':
        #     result = True
        result = result1 and result2
        print('TME_Exclusion_Length is {0}'.format(TME_Exclusion_Length))
        self.bios_conf.bios_back_home()
        return result

    def change_dimm_management(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Socket Configuration',
                                           'Memory Configuration', 'Memory Dfx Configuration'])
        result_process(result, 'Enter Memory Dfx Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select("DIMM Management", "BIOS Setup")
        result_process(result, "Change DIMM Management Frome DDRT DIMM Management Driver to BIOS Setup")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def disable_Appdirect(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Socket Configuration',
                                           'Memory Configuration', 'Memory Dfx Configuration'])
        result_process(result, 'Enter Memory Dfx Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select("AppDirect", "Disable")
        result_process(result, "Disable AppDirect")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def change_tme_exclusion(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Socket Configuration',
                                           'Processor Configuration', 'Processor Dfx Configuration'])
        result_process(result, 'Enter Processor Dfx Configuration')
        result = self.bios_conf.bios_opt_textbox_input("TME Exclusion Base Address Increment Value", "2000")
        result_process(result, "Change  TME Exclusion Base ot [2000]")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Socket Configuration',
                                           'Processor Configuration', 'Processor Dfx Configuration'])
        result_process(result, 'Enter Processor Dfx Configuration')
        result = self.bios_conf.bios_opt_textbox_input("TME Exclusion Length Increment value", "1000")
        result_process(result, "Change  TME Exclusion Length Increment Value ot [1000]")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def enter_bios_option(self, option):
        result = self.bios_conf.bios_menu_navi(option)
        return result

    def run_redhat_cmd(self, command):
        return ssh.ssh_connect(command, self.sut_ip, self.LN_USERNAME, self.LN_PASSWORD)

    def check_eps_menu(self):
        reboot_cmd = 'echo {0} | sudo -S reboot'.format(self.LN_PASSWORD)
        self.run_redhat_cmd(reboot_cmd)
        boot_to_setup = self.bios_conf.enter_bios(f2_timeout=F2_TIMEOUT)
        result_process(boot_to_setup, 'Reboot to BIOS setup.')
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'TCG2 Configuration'])
        result_process(result, 'Enter EDKII Menu->TCG2 Configuration')
        tpm_opt = self.bios_conf.bios_opt_get_drop_down_values('TPM2 Operation')
        tpm_opt_lower = list(map(lambda x: x.lower(), tpm_opt))
        step_string = 'Check TPM2_ChangeEPS menu, this menu should be shown.'
        result_process('TPM2 ChangeEPS'.lower() in tpm_opt_lower, step_string, is_step_complete=True)

    def get_value_status(self, serial_log, key1, key2, key3):
        result1 = False
        result2 = False
        result3 = False
        lines = serial_log.split('\r\n')
        for line in lines:
            if key1 in line:
                result1 = True
                break
        for line in lines:
            if key2 in line:
                result2 = True
                break
        for line in lines:
            if key3 in line:
                result3 = True
                break
        result = result1 and result2 and result3
        return result

    def flash_ifwi_image(self):
        if not lib_flash_server.flashifwi_em100(self.ifwi, soundwave_port=self.soundwave_port, binary=self.ifwi):
            result_process(False, 'flash ifwi')
        else:
            result_process(True, 'flash ifwi')
    #
    # def flash_bmc_image(self):
    #     if not lib_flash_server.flash_bmc(self.bmc, binary=self.sf600_binary, soundwave_port=self.soundwave_port):
    #         result_process(False, 'flash bmc')
    #         return False
    #     else:
    #         result_process(True, 'flash bmc')
    #         return True
    #
    # def flash_cpld_image(self):
    #     # step Pre requisite flash CPLD
    #     if not lib_flash_server.flash_cpld(self.cpld, soundwave_port=self.soundwave_port,
    #                                        binary=self.quartus_pgm_binary,
    #                                        jtag_binary=self.jtag_binary,
    #                                        expect_cables=self.expect_cables,
    #                                        regex_device=self.regex_device):
    #         result_process(False, 'flash CPLD')
    #         return False
    #     else:
    #         result_process(True, 'flash CPLD')
    #         return True

    def bios_enable_pfr(self):
        self.bios_conf.bios_back_home()
        self.bios_conf.bios_menu_navi(["EDKII Menu", "Platform Configuration", 'Miscellaneous Configuration'])
        self.bios_conf.bios_opt_drop_down_menu_select('PFR Provision', 'Enable')
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()
        self.bios_conf.reset_system()
        result = self.bios_conf.enter_bios(f2_timeout=F2_TIMEOUT)
        return result

    def check_pfr_status(self, expect_status='<Yes>'):
        self.bios_conf.bios_back_home()
        self.bios_conf.bios_menu_navi(
            ["EDKII Menu", "Platform Configuration", 'Miscellaneous Configuration'])
        pfr_provision_value = self.bios_conf.get_system_information(
            'PFR Status: Provisioned')
        if pfr_provision_value == expect_status:
            result_process(True,
                           'Check PFR,actual value:{0}, expect value:{1}'.format(pfr_provision_value, expect_status))
            return True
        else:
            result_process(False,
                           'Check PFR, actual value:{0}, expect value:{1}'.format(pfr_provision_value, expect_status),
                           test_exit=False)
            return False

    def check_pfr_prov_lock(self, prov_status='<Yes>', lock_status='<Yes>'):
        # boot to BIOS setup
        result = self.bios_conf.enter_bios(f2_timeout=F2_TIMEOUT)
        result_process(result, 'Enter BIOS setup')
        self.bios_conf.bios_menu_navi(
            ["EDKII Menu", "Platform Configuration", 'Miscellaneous Configuration'])
        pfr_provision_value = self.bios_conf.get_system_information(
            'PFR status: Provisioned')
        pfr_lock_value = self.bios_conf.get_system_information('PFR status: Locked')
        result_process(pfr_provision_value == prov_status,
                       'Check PFR Prov:{0}'.format(pfr_provision_value),
                       is_step_complete=True, test_exit=False)
        result_process(pfr_lock_value == lock_status, 'Check PFR Lock:{0}'.format(pfr_lock_value),
                       is_step_complete=True)

    def run_ib_cmd(self, param_dict, ota_cmd):
        self.bios_conf.efi_shell_cmd('cd {0}'.format(param_dict['OTA_Tool_Folder']), time_out=10)
        ota_log = self.bios_conf.efi_shell_cmd(ota_cmd, time_out=15)
        result_process(True, 'run ota cmd:{0}'.format(ota_cmd), is_step_complete=True)
        return ota_log

    def get_bios_tme_status(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->Processor Configuration")
        TME_status = self.bios_conf.get_system_information('Total Memory Encryption (TME)')
        return TME_status

    def get_bios_mktme_status(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->Processor Configuration")
        MKTME_status = self.bios_conf.get_system_information('Total Memory Encryption Multi-Tenant(TME-MT)')
        print('MKTME_status is {0}'.format(MKTME_status))
        return MKTME_status

    def bios_disable_limit_cpu(self):
        self.bios_conf.bios_back_home()
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Socket Configuration', 'Processor Configuration'])
        result_process(result, 'Processor Configuration')
        cpu_value = self.bios_conf.get_system_information('Limit CPU PA to 46 bits')
        if cpu_value == '<Enable>':
            self.bios_conf.bios_opt_drop_down_menu_select('Limit CPU PA to 46 bits', 'Disable')
        self.bios_conf.bios_save_changes()

    def bios_disable_eop(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Platform Configuration', 'Server ME Debug Configuration',
                                           'Server ME General Configuration'])
        result_process(result, 'Enter Server ME General Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select('END_OF_POST Message', 'Disabled')
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def bios_set_bmc_user(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Platform Configuration',
                                           'BMC LAN Configuration', 'User Configuration'])
        result_process(result, 'Enter User Configuration')
        result = self.bios_conf.bios_opt_drop_down_menu_select('Enable Complex Password', 'Enabled')
        result_process(result, 'Set Enable Complex Password=Enabled')
        result = self.bios_conf.bios_opt_drop_down_menu_select('Privilege', 'Administrator')
        result_process(result, 'Set User Privilege=Administrator')
        result = self.bios_conf.bios_opt_drop_down_menu_select('User Status', 'Enabled')
        result_process(result, 'Set User Status=Enabled')
        result = self.bios_conf.bios_opt_dialog_box_input('User Name', BMC_USER_NAME)
        result_process(result, 'Set BMC User name: {0}'.format(BMC_USER_NAME))
        self.bios_conf.press_menu('User Password', index=2)
        result = self.bios_conf.dialog_box_interaction(BMC_PWD)
        self.bios_conf.bios_control_key_press('ENTER')
        # confirm new password
        result = result and self.bios_conf.dialog_box_interaction(BMC_PWD)
        self.bios_conf.bios_control_key_press('ENTER')
        result_process(result, 'Set BMC User Password:{0}'.format(BMC_PWD))
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def bios_get_bmc_ip(self):
        result = self.bios_conf.bios_menu_navi(['EDKII Menu', 'Platform Configuration', 'BMC LAN Configuration'])
        result_process(result, 'Enter BMC LAN Configuration')
        bmc_ip = self.bios_conf.get_system_information('IP Address', index_to_query=2)
        self.bios_conf.bios_back_home()
        if bmc_ip == '0.0.0.0':
            result_process(False, 'BMC IP is 0.0.0.0, please check the network')
        else:
            result_process(True, 'BMC IP : {0}'.format(bmc_ip))
        return bmc_ip

    def run_oob_cmd(self, ipmi_cmd):
        ssh_cmd = "echo y | {0} -ssh {1}@{2} -pw {3}".format(self.PLINK_PATH, self.OOB_HOST_USER, self.OOB_HOST_IP,
                                                             self.OOB_HOST_PWD)
        cmd = ssh_cmd + ' ' + ipmi_cmd
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate(timeout=10)[0]
        print(output)
        return output

    @staticmethod
    def check_oob_respond(output, value1, value2, value3):
        output_list = output.strip().split(b' ')
        a = str(output_list[13], encoding='utf8')
        b = str(output_list[17], encoding='utf8')
        c = str(output_list[19], encoding='utf8')
        result1 = a == value1
        result2 = b == value2
        result3 = c == value3
        d = '{0}:{3}  {1}:{4}  {2}:{5}'.format(value1, value2,value3, a, b, c)
        print(d, result1, result2, result3)
        result = result1 and result2 and result3
        return result

    def check_bios_txt_status(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration", "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->Processor Configuration")
        txt_status = self.bios_conf.get_system_information('Enable Intel(R) TXT')
        vmx_status = self.bios_conf.get_system_information('VMX')
        smx_status = self.bios_conf.get_system_information('Enable SMX')
        msr_status = self.bios_conf.get_system_information('MSR Lock Control')
        self.bios_conf.bios_back_home()
        return (txt_status, vmx_status, smx_status, msr_status)

    def bios_enable_sgx(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration",
                                           "Processor Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->"
                               "Processor Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("Total Memory Encryption (TME)", "Enable")
        result_process(result, "Enable TME")
        result = self.bios_conf.bios_opt_drop_down_menu_select("SW Guard Extensions (SGX)", "Enable")
        result_process(result, "Enable SGX")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()

    def bios_disable_uma_base(self):
        result = self.bios_conf.bios_menu_navi(["EDKII Menu", "Socket Configuration",
                                           "Common RefCode Configuration"])
        result_process(result, "Enter EDKII Menu->Socket Configuration->"
                               "Common RefCode Configuration")
        result = self.bios_conf.bios_opt_drop_down_menu_select("UMA-Based Clustering", "Disable   (All2All)")
        result_process(result, "Disable UMA-Based")
        self.bios_conf.bios_save_changes()
        self.bios_conf.bios_back_home()


def main(obj, timeout):
    def _catch_exception():
        serial_trace = SerialTrace(obj.case_path, obj.TEST_CASE_ID)
        try:
            serial_trace.start_capture_trace()
            obj.run()
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: %s" % e, obj.TEST_CASE_ID, obj.SCRIPT_ID)
            result_process(False, "EXCEPTION: %s" % e)
        finally:
            serial_trace.capture_tag = False
            obj.tear_down()

    exec_thread = threading.Thread(target=_catch_exception)
    exec_thread.setDaemon(True)
    exec_thread.start()
    exec_thread.join(timeout)
    if exec_thread.is_alive():
        result_process(False, 'execution timeout')
    if IS_CASE_PASS:
        library.write_log(lib_constants.LOG_PASS, "PASS: Test case is successful", obj.TEST_CASE_ID, obj.SCRIPT_ID)
    else:
        sys.exit(lib_constants.EXIT_FAILURE)


if __name__ == '__main__':
    # trace_name = os.path.basename(os.path.dirname(os.path.realpath(__file__))) \
    #              + '_serial_trace_' + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + '.txt'
    # trace_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), trace_name)
    # print(trace_name)
    new_name = 'PFR_Info_' + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + '.txt'
    backup_pfr_info_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), new_name)
    print(backup_pfr_info_txt)

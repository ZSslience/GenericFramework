import os
import wmi
from SoftwareAbstractionLayer import lib_parse_config


class WmiHandler:
    def __init__(self):
        """
        Function Name       : __init__()
        Parameters          : None
        Functionality       : Initialize WMI parameters for connection
        Function Invoked    : wmi
        Return Value        : None
        """
        self._SUT = {
            'HOST': None,
            'USER': None,
            'PSWD': None
        }
        SUT_CONFIG = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), os.path.pardir,
            r"SoftwareAbstractionLayer\system_configuration.ini")
        config = lib_parse_config.ParseConfig()
        sut_host = str(config.get_value(
            SUT_CONFIG, 'SSH Configuration', 'HOST'))
        sut_user = str(config.get_value(
            SUT_CONFIG, 'SSH Configuration', 'USER'))
        sut_pswd = str(config.get_value(
            SUT_CONFIG, 'SSH Configuration', 'PASS'))
        self._SUT['HOST'] = sut_host
        self._SUT['USER'] = sut_user
        self._SUT['PSWD'] = sut_pswd

    def wmi_pnpd_opt(self, local=True, entry=""):
        """
        Function Name       : wmi_pnpd_opt()
        Parameters          :
                local       : bool  - Connect local or remote machine
                              value | True(*), False
                entry       : str   - plug and play device string to query 
        Functionality       : A WMI connection wrapper to handle local or
                              remote plug and play device query.
        Function Invoked    : wmi.WMI()
        Return Value        : [(index, name, category, manufacturer,
                              CompatibleID, DeviceID, (HardwareID),
                              YellowBangCode)]
                              (HardwareID)
                              (enumerator\\enumerator-specific-device-ID,
                              *enumerator-specific ID, device-class-specific ID)
                              i.e:
                              as matched item(s) returned in list once success.
                              system-error-codes for failure.
        """
        os_ns = "root/cimv2"
        pnpd_return = []
        num = 0
        con = self._wmi_connect(i_ns=os_ns,
                                local=local,
                                imp_level='impersonate',
                                auth_level='pktPrivacy')
        pnp_entity = con.Win32_PnPEntity()
        for device in pnp_entity:
            if entry in str(device.Name):
                pnpd_return.append((pnp_entity.index(device),
                                    device.Name,
                                    device.PNPClass,
                                    device.Manufacturer,
                                    device.CompatibleID[0],
                                    device.DeviceID,
                                    device.HardwareID,
                                    device.ConfigManagerErrorCode))
            else:
                num += 1
        if num == len(pnp_entity):
            return False
        else:
            print('Device %s: Matched with: %s' % (entry, pnpd_return))
            return pnpd_return

    def wmi_os_opt(self, local=True, os_instruct=None):
        """
        Function Name       : wmi_os_opt()
        Parameters          :
                local       : bool  - Connect local or remote machine
                              value | True(*), False
                os_instruct : str   - Using the Instruction List to check
                                      supported operation via this function
                                      *Instruction List*
                              (Bool)  reboot: Apply system reboot
                              (Bool)  shutdown: Apply system shutdown
                              (str)   name: Check Windows Version
        Functionality       : A WMI connection wrapper to handle local or
                              remote OS check or operations.
        Function Invoked    : wmi.WMI()
        Return Value        : [(int)] 0 or ['str'] for success or
                              system-error-codes for failure
        """
        os_ns = "root/cimv2"
        con = self._wmi_connect(i_ns=os_ns,
                                local=local,
                                imp_level='impersonate',
                                auth_level='pktPrivacy')
        # WQL query to fetch Win32_OperatingSystem object.
        wql = "select * from Win32_OperatingSystem where Primary=true"
        # os_con provides a list object as Win32_OperatingSystem
        # operatable methods
        os_con = con.query(wql)
        os_return = []
        for _ot in os_con:
            if os_instruct == "reboot":
                os_sd = _ot.Reboot()[0]
            elif os_instruct == "shutdown":
                os_sd = _ot.Shutdown()[0]
            elif os_instruct == "name":
                os_sd = _ot.Name
            else:
                pass
            os_return.append(os_sd)
        print('OS Operation %s: %s' % (os_instruct, os_return))
        return os_return

    def wmi_tpm_check(self, local=True, tpm_instruct=None):
        """
        Function Name       : wmi_tpm_check()
        Parameters          :
                local       : bool  - Connect local or remote machine
                              value | True(*), False
                tpm_instruct: str   - Using the Instruction List to check
                                      supported operation via this function
                                      *Instruction List*
                              (Bool)  isActivated: Check TPM activate state
                              (Bool)  isEnabled: Check TPM enable state
                              (Bool)  isOwned: Check TPM own state
                              (Bool)  isReady: Check TPM Ready state
                              (Bool)  isAutoProvEn: Check TPM auto provision
                                      enable state
                              (str, Bool)  isReadyinfo: Check TPM isReady
                                      information i.e: (0, True)
                              (str)   mftrId: Show Manufacturer Id
                              (str)   mftrVer: Show Manufacturer Version
                              (str)   mftrVerI: Show Manufacturer Version Info
                              (str)   phyPreVerI: Show Physical Presence
                                      Version Info
                              (str)   specVer: Show Spec Version
        Functionality       : A WMI connection wrapper to handle local or
                              remote TPM check or operations.
        Function Invoked    : wmi.WMI()
        Return Value        : [(bool)/(str)] of check or operation results
        """
        tpm_ns = "root/cimv2/security/microsofttpm"
        con = self._wmi_connect(tpm_ns, local,
                                imp_level='impersonate',
                                auth_level='pktPrivacy')
        tpm_con = con.Win32_Tpm()
        tpm_return = []

        def _tpm_check_opt(tpm_target=object, _idx=0):
            _opt_dict = {
                "isReady": tpm_target.IsReady()[_idx],
                "isActivated": tpm_target.IsActivated_InitialValue,
                "isEnabled": tpm_target.IsEnabled_InitialValue,
                "isOwned": tpm_target.IsOwned_InitialValue,
                "isAutoProvEn": tpm_target.IsAutoProvisioningEnabled()[_idx],
                "isReadyinfo": tpm_target.IsReadyInformation()[:-1],
                "mftrId": tpm_target.ManufacturerId,
                "mftrVer": tpm_target.ManufacturerVersion,
                "mftrVerI": tpm_target.ManufacturerVersionInfo,
                "phyPreVerI": tpm_target.PhysicalPresenceVersionInfo,
                "specVer": tpm_target.SpecVersion
            }
            tpm_r = _opt_dict[tpm_instruct]
            return tpm_r
        for _tt in tpm_con:
            tpm_return.append(_tpm_check_opt(_tt))
        print('TPM %s: %s' % (tpm_instruct, tpm_return))
        return tpm_return

    def _wmi_connect(self, i_ns="", local=True,
                     imp_level=None, auth_level=None):
        """
        Function Name       : _wmi_connect()
        Parameters          :
                i_ns        : str   - Namespace to be queried
                              value | None(*)
                              i.e: root/cimv2/security/microsofttpm
                local       : bool  - Connect local or remote machine
                              value | True(*), False
                imp_level   : str   - ImpersonationLevel in WMI
                              value | None(*)/anonymous/identify/
                                      impersonate/delegate
                auth_level  : str   - AuthenticationLevel in WMI
                              value | None(*)/default/connect/call/
                                      pkt/pktIntegrity/pktPrivacy
        Functionality       : A WMI connection wrapper to handle local or
                              remote device with namespace provided.
        Function Invoked    : wmi.WMI()
        Return Value        : connected Object
        """
        if local:
            sut_ip_address = None
            sut_user = None
            sut_pass = None
            sut_ns = i_ns
        else:
            sut_ip_address = self._SUT['HOST']
            sut_user = self._SUT['USER']
            sut_pass = self._SUT['PSWD']
            sut_ns = i_ns
        try:
            con = wmi.WMI(computer=sut_ip_address,
                          user=sut_user,
                          password=sut_pass,
                          impersonation_level=imp_level,
                          authentication_level=auth_level,
                          namespace=sut_ns)
            return con
        except Exception as e:
            print('WMI Connection Failed: %s' % (e))


if __name__ == "__main__":
    opt = WmiHandler()
    tpm_rs = opt.wmi_tpm_check(local=False, tpm_instruct="isReady")
    tpm_as = opt.wmi_tpm_check(local=False, tpm_instruct="isActivated")
    tpm_es = opt.wmi_tpm_check(local=False, tpm_instruct="isEnabled")
    tpm_os = opt.wmi_tpm_check(local=False, tpm_instruct="isOwned")
    tpm_ape = opt.wmi_tpm_check(local=False, tpm_instruct="isAutoProvEn")
    tpm_ri = opt.wmi_tpm_check(local=False, tpm_instruct="isReadyinfo")
    print(tpm_ri[0] == (0, True))
    tpm_mid = opt.wmi_tpm_check(local=False, tpm_instruct="mftrId")
    tpm_mv = opt.wmi_tpm_check(local=False, tpm_instruct="mftrVer")
    tpm_mvi = opt.wmi_tpm_check(local=False, tpm_instruct="mftrVerI")
    tpm_ppvi = opt.wmi_tpm_check(local=False, tpm_instruct="phyPreVerI")
    tpm_sv = opt.wmi_tpm_check(local=False, tpm_instruct="specVer")
    pnp_nam = opt.wmi_pnpd_opt(local=False, entry="PCI Serial Port")
    print(pnp_nam[0][-1])
    os_nam = opt.wmi_os_opt(local=False, os_instruct="name")
    print("Windows" in os_nam[0])
    # os_rbt = opt.wmi_os_opt(local=False, os_instruct="reboot")
    # os_std = opt.wmi_os_opt(local=False, os_instruct="shutdown")
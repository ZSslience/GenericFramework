import os
import paramiko
from SoftwareAbstractionLayer import lib_parse_config

def connection_init():
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
    sut_ip = sut_host
    sut_port = 22
    sut_username = sut_user
    sut_password = sut_pswd
    scp = paramiko.Transport((sut_ip, sut_port))
    scp.connect(username=sut_username, password=sut_password)
    sftp = paramiko.SFTPClient.from_transport(scp)
    return sftp


def remote_fetch(f_remote, f_local):
    """
    Function Name       : remote_fetch()
    Parameters          : f_remote(str): absolute remote file path to fetch
                          f_local(str): absolute local file path to save
    Functionality       : Remote file fetch via SSH with list returned
    Function Invoked    : paramiko, lib_parse_config
    Return Value        : list of file content split with newlines
    """
    sftp = connection_init()
    remote_file = f_remote
    local_file = f_local
    try:
        sftp.get(remote_file, local_file)
        with open(local_file, 'rb') as buf:
            buf_list = buf.readlines()
            return buf_list
    except Exception:
        return False


def remote_put(f_local, f_remote):
    """
    Function Name       : remote_put()
    Parameters          : f_remote(str): absolute remote file path to fetch
                          f_local(str): absolute local file path to save
    Functionality       : Remote file put via SSH
    Function Invoked    : paramiko, lib_parse_config
    Return Value        : True success, False failed
    """
    sftp = connection_init()
    remote_file = f_remote
    local_file = f_local
    try:
        sftp.put(local_file, remote_file)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    r_file = r"p:\ath\to\remote\file"
    l_file = r"p:\ath\to\local\file"
    remote_fetch(r_file, l_file)

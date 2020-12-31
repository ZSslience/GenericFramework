__author__ = "Deepankar Borgohain"
#!/usr/pkg/bin/python
import paramiko
import time
import library
import lib_constants
import os
import configparser
## Move to be SAL in INI file
SUT_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__),'system_configuration.ini'))
SUT_CONFIG_CLIENTS = r'C:\Testing\GenericFramework\SoftwareAbstractionLayer\system_configuration.ini'
config = configparser.ConfigParser()
config.read(SUT_CONFIG_CLIENTS)
(config.sections())
HOST = (config.get('SSH Configuration','HOST'))
USER = (config.get('SSH Configuration','USER'))
PASS = (config.get('SSH Configuration','PASS'))

                                                                                 #setting parameters like host IP, username, passwd and number of iterations to gather cmds
########################################################################################################
#  Function     : ssh_connect
#  Parameter    : None
#  Purpose      : Used to connect the Ethernet port using ssh by providing the
                  #username, password and Host id.
#  Return       : RET_SUCCESS:    the target item is selected
#                 RET_TEST_FAIL:  item can not be found
#                 RET_ENV_FAIL:   any exception
#                 RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
#  Dependencies : None
#  Additional Info :  SUT_config.cfg file contains the user name, password and Host name.
#Example usage : ssh_connect('lss',"10.223.244.83","vm16","intel@123")
                                                                                #A function that logins and execute commands
def ssh_connect(cmd,__host=HOST,__user=USER,__password=PASS):
  client1=paramiko.SSHClient()
  client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())                 #Add missing client key
  client1.connect(__host,username=__user,password=__password)                             #connect to switch
  library.write_log(lib_constants.LOG_INFO,"SSH connection to %s established" %__host,"None","None")
  library.write_log(lib_constants.LOG_INFO,"Executing : {0}" .format(cmd), "None", "None")
  stdin, stdout, stderr = client1.exec_command(cmd)                             #Gather commands and read the output from stdout
  val = stdout.read()
  val_err = stderr.read()
  library.write_log(lib_constants.LOG_INFO, '{0}'.format(val),"None","None")
  library.write_log(lib_constants.LOG_DEBUG, '{0}'.format(val_err), "None", "None")
  client1.close()
  return val


















"""
Performs to read and parse the config file.
For python 2.* version need pip install configparser.
Title      	: lib_parse_config.py
Author(s)  	: Liang Yan
Description	: Things to perform:
            1. Check the config file if can be read and parsed
            2. Get the value by given option name
"""
import ast
import os
import configparser
import lib_constants


class ParseConfigError(Exception):
    """This is base class for exceptions in parsing config file"""
    pass


class ParseConfig(object):
    def __init__(self):
        object.__init__(self)

    @staticmethod
    def parse_config_file(config_file):
        """
        Function Name       : parse_config_file
        Parameters          : config_file
        Functionality       : Check if config file exists and can ba parsed successfully
        Function Invoked    : None
        Return Value        : Return instance object of configparser if config file exists and can be parsed
                              successfully, else raise exception.
        """
        try:
            config = configparser.ConfigParser()
            with open(config_file) as f:
                config.read_file(f)
        except IOError as e:
            raise ParseConfigError('ERROR opening config file\n%s' % e)
        except configparser.ParsingError as e:
            raise ParseConfigError('ERROR parsing config file\n%s' % e)
        return config

    def get_value(self, config_file, sectionname, optionname, abort_on_failure=True):
        """
        Function Name       : get_value
        Parameters          : config_file, sectionname, optionname
        Functionality       : Get option name value from config file, if exists return the value
        Function Invoked    : parse_config_file(config_file)
        Return Value        : the value of the option name if exist, else raise exception
        """
        try:
            config = self.parse_config_file(config_file)
            value = config.get(sectionname, optionname)
        except(configparser.NoSectionError, configparser.NoOptionError, ParseConfigError) as e:
            if abort_on_failure:
                raise ParseConfigError('ERROR getting value from config \n%s' % e)
            else:
                return None
        return value

    def set_value(self, config_file, sectionname, optionname, value, abort_on_failure=True):
        """
        Function Name       : set_value
        Parameters          : config_file, sectionname, optionname, value
        Functionality       : Set option name value to config file, if success return the True
        Function Invoked    : parse_config_file(config_file)
        Return Value        : True if success, else raise exception
        """
        try:
            config = self.parse_config_file(config_file)
            config.set(sectionname, optionname, value)
            with open(config_file, 'w+') as f:
                config.write(f)
        except(configparser.NoSectionError, configparser.NoOptionError, ParseConfigError) as e:
            if abort_on_failure:
                raise ParseConfigError('ERROR setting value from config \n%s' % e)
            else:
                return False
        return True

    def get_value_with_type(self, config_file, sectionname, optionname, abort_on_failure=True):
        """
        Function Name       : get_value_with_type
        Parameters          : config_file, sectionname, optionname
        Functionality       : Get option name value with variable type from config file, if exists return the value
                               [section]          // variable type will return:
                                key1 = 123        //  int
                                key2 = [1,2,3]    //  list
                                key3 = 'hello'    //  str
                                key4 = {1:0}      //  dic

        Function Invoked    : parse_config_file(config_file)
        Return Value        : the value of the option name with variable type if exist, else raise exception
        """
        try:
            config = self.parse_config_file(config_file)
            value = ast.literal_eval(config.get(sectionname, optionname))
        except(configparser.NoSectionError, configparser.NoOptionError, ParseConfigError) as e:
            if abort_on_failure:
                raise ParseConfigError('ERROR getting value from config \n%s' % e)
            else:
                return None
        return value

    def ReadConfig(self, sectionname, optionname):
        middleware_config = os.path.join(lib_constants.MIDDLEWARE_PATH, 'Config.ini')
        script_config = os.path.join(lib_constants.SCRIPTDIR, 'Config.ini')
        value = self.get_value(middleware_config, sectionname, optionname, abort_on_failure=False)
        if value is None:
            return self.get_value(script_config, sectionname, optionname, abort_on_failure=False)
        return value



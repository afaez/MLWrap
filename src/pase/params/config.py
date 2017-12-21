import configparser
import os
import pase.constants.error_msg as error

app_path = os.getenv("MLWRAP_PATH")
if app_path is None:
    raise EnvironmentError(error.const.environment_variable_is_not_set.format("MLWRAP_PATH"))

whitelist_config = configparser.ConfigParser()
whitelist_config.read(app_path + "/conf/whitelist.ini")


def get_parameter_value(config, section, parameter):
    section = config[section]
    if parameter in section:
        return section[parameter]


def is_in_whitelist(class_path):
    value = get_parameter_value(whitelist_config, "whitelist", class_path)
    if value == "True":
        return True
    else:
        return False

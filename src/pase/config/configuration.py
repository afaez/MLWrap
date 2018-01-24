import os
import pase.constants.error_msg as error
import logging
import json


# Get the path to the configurations
app_path = os.getenv("PASE_CONFIG_PATH")
if app_path is None:
    app_path = ".."
    #raise EnvironmentError(error.const.environment_variable_is_not_set.format("PASE_CONFIG_PATH"))
# load classes.json
_classes_file = open(app_path + "/conf/classes.json")
CLASSES_DICT = json.load(_classes_file)
_classes_file.close()


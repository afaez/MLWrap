""" Offers configuration lookups.
"""
from . import configuration

def getclassesdirectoryentry(class_path):
    """ Returns the dictionary entry. 
    """
    if class_known(class_path):
        return configuration.CLASSES_DICT[class_path]
    else:
        # Return an empty dictionary entry.
        return {}

def class_known(class_path):
    """ Returns true if the class_path is defined in the classes.json configuration.
    """
    class_path = class_path.partition(".__construct")[0] # delete '.__construct' from class_path
    return class_path in configuration.CLASSES_DICT

def has_wrapper(class_path):
    """ Returns true if in the classes.json configuration the class_path is set to be wrapped.
    This method assumes that class_known(class_path) returns True.
    """
    return "wrapper" in getclassesdirectoryentry(class_path)

def get_wrapper(class_path):
    """ Returns the wrapper classpath for the class_path.
    This method assumes that has_wrapper(class_path) returns True.
    """
    return getclassesdirectoryentry(class_path)["wrapper"]

def fullname(callable_path):
    """ Returns the fully qualified name of the instance returned by callable.
    """
    # if the class_path is 
    if class_known(callable_path):
        if "class_path" in configuration.CLASSES_DICT [callable_path]:
            return configuration.CLASSES_DICT [callable_path]["class_path"]
        else:
            return callable_path
    return None

def check_type(type_string):
    """ Checks the given type string.
    """
    return True # TODO implement typing system

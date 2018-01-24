""" Offers configuration lookups.
"""
from . import configuration

def getclassesdirectoryentry(classname):
    """ Returns the dictionary entry. 
    """
    if class_known(classname):
        return configuration.CLASSES_DICT[classname]
    else:
        # Return an empty dictionary entry.
        return {}

def class_known(classname):
    """ Returns true if the classname is defined in the classes.json configuration.
    """
    return classname in configuration.CLASSES_DICT

def has_wrapper(classname):
    """ Returns true if in the classes.json configuration the classname is set to be wrapped.
    This method assumes that class_known(classname) returns True.
    """
    return "wrapper" in getclassesdirectoryentry(classname)

def get_wrapper(classname):
    """ Returns the wrapper classpath for the classname.
    This method assumes that has_wrapper(classname) returns True.
    """
    return getclassesdirectoryentry(classname)["wrapper"]

def fullname(callable_path):
    """ Returns the fully qualified name of the instance returned by callable.
    """
    # if the class_path is 
    if class_known(callable_path):
        if "classname" in configuration.CLASSES_DICT [callable_path]:
            return configuration.CLASSES_DICT [callable_path]["classname"]
        else:
            return callable_path
    return None

def check_type(type_string):
    """ Checks the given type string.
    """
    return True # TODO implement typing system

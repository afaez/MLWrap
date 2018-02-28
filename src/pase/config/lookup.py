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

def method_defined(class_path, method_name):
    """ Returns true if the classpath is defined in the classes configuration and if the methods name is defined in its 'methods' field.
    """
    if not class_known(class_path):
        return False
    classconfig = getclassesdirectoryentry(class_path)

    if "methods" in classconfig:
        return method_name in classconfig["methods"]
    else:
        return True

def get_methods(class_path):
    """ Returns the dictionary containing the methods of the class path.
    """
    classconfig = getclassesdirectoryentry(class_path)
    if "methods" in classconfig:
        return classconfig["methods"]
    else:
        return dict()

def method_returntype(class_path, method_name):
    """ Returns true if the method is included in the methods field of the classpath.
    If no methods field is defined all methods are allowed.
    """
    methods = get_methods(class_path)
    if method_name in methods:
        return methods[method_name]["return_type"]
    else:
        return None


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

def check_inheritance(base_name, super_name):
    baseDef = getclassesdirectoryentry(base_name)
    if "extends" in baseDef:
        if super_name in baseDef["extends"]:
            return True
        else:
            for parent in baseDef["extends"]:
                if check_inheritance(parent, super_name):
                    return True

    return False

def allsubtypes(super_name, ignore_superficial_types=True):
    for base_name in configuration.CLASSES_DICT:
        if ignore_superficial_types and base_name[0] == '$':
            continue
        if check_inheritance(base_name, super_name):
            yield base_name
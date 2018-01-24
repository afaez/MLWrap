from .reflector import fullname, call
from . import reflector, wrapreflector
from pase import config

def construct(class_path_list, kwargs):
    """ Masks the two construct methods from reflector and wrapreflector.
    """
    class_path_string = ".".join(class_path_list)
    if not config.lookup.class_known(class_path_string):
        raise ValueError("Class not defined in configuration")
    if not config.lookup.has_wrapper(class_path_string):
        # doesnt have a wrapper.. do normal reflection construct:
        return reflector.construct(class_path_list, kwargs)
    else:
        # else : the class_path has to be wrapped
        return wrapreflector.construct(class_path_list, kwargs)


import inspect
import pase.config
import logging
from importlib import \
    import_module  # used to dereference module names. see function: construct
from inspect import \
    signature  # used to inspect function signature. see function: _validate_parameters

import pase.constants.error_msg as error  # Contains error messages constants.

def _extract_arglist(kwargs):
    """ Extracts '$arglist$' array from kwargs dictionary. 
    If kwargs['$arglist$'] doesn't map to a list, this method returns an empty list
    """
    args = []
    if( "$arglist$" in kwargs):
        args = kwargs["$arglist$"]
    if args is None or not isinstance(args, list):
        # Defaults to empty argument list if there was any problem
        args = []
    return args

def validate_parameters(given_param, callable_, weak = False):
    """ validates the parameters from the given_param and fills it with the argument from given_param_list and returns a clean paramter dictionary which matches the signature of the callable_.
    Parameters:
        given_param: Dictionary given to call the callable_
        callable_: Python callable object. Can be a function or a constructor. 
        weak: if true, is doesn't check if every necessary argument is found in given_param.
    Returns: 
        A sanitized parameter dictionary that can be used to call the callable_.
    Raises:
        ValueError, if there is a parameter in callable's signature that is mandatory and given_param doesn't contain it.
    """
     # Now create a validated dictionary based on the signature from the method: 
    validated_dict = {}
    signature_ = signature(callable_)
    if(given_param is None):
        given_param = {}
    # Extract args from kwargs
    # given_param_list: contains the list of positional arguments which are given by the client.
    given_param_list = _extract_arglist(given_param)
    # iterate over every parameter:
    for param_key in signature_.parameters:
        if len(given_param_list) > 0: # there are still positional arguments to be dealt with
            # Delete positional arguments until its empty.
            argument = given_param_list.pop(0) # extract first argument.
            validated_dict[param_key] = argument # add the argument to the validated list

        elif(param_key in given_param):
            # Copy parameters to the validated dictionary:
            validated_dict[param_key] = given_param[param_key]

        elif(not weak and signature_.parameters[param_key].default == inspect._empty): # No default is set.
            # The parameter wasn't sent by the client. 
            raise ValueError(error.const.parameter_is_mandatory.format(f"{param_key}"))
    logging.debug("validated dict: " + str(validated_dict.keys()))
    return validated_dict

def fullname(o):
    """ Get fully qualified class name of an object o.
    """
    try:
        return o.__module__ + "." + o.__class__.__name__
    except AttributeError: # o object has no attribute '__module__'
        return o.__class__.__name__

def traverse_package(package_path, package_string = ""):
        """ Recursively traverses package_path list and calls traverse_module.
        """
        def traverse_module(package_path, module):
            """ Recursevly traverses package_path until it its empty and the module is found. Else None is returned.
            """
            if not package_path:
                return module
            attribute = package_path[0]
            if hasattr(module, attribute):
                return traverse_module(package_path[1:], getattr(module, attribute))
            else:
                return None

        package_string = package_string + package_path[0]
        package_path = package_path[1:]
        if not package_path:
            return None
        package = import_module(package_string)
        attribute = package_path[0]
        if hasattr(package, attribute):
            module = traverse_module(package_path[1:], getattr(package, attribute))
            if module:
                return module
        else:
            return traverse_package(package_path, package_string + ".")

    
    
def construct(package_path, kwargs):
    """ Dereferences a callable by its package_path and calls it using the given parameters.
    """ 
    try:
        module = traverse_package(package_path)
    except ModuleNotFoundError as ex:
        raise ValueError(f"{ex}")

    if not module:
        # No module found.
        raise ValueError(error.const.module_not_found.format(".".join(package_path)))
    try: 
        clazz = module
        if(not callable(clazz)):
            raise ValueError(error.const.cannot_construct_class_name.format(clazz.__name__,".".join(package_path)))
        # Validate the parameters:
        validated_args = validate_parameters(kwargs, clazz)
        # Call the constructor:
        instance = clazz(**validated_args)
        return instance, fullname(instance)
    except AttributeError as e:
        logging.error(e, exc_info=True)
        raise e #ValueError(error.const.class_not_found_in_module.format( class_name, module_name))
    

def call(instance, method_name, parameters = {}):
    """ call is used to access a instance's method or field.
    Parameters:
        instance: Python object whose attribute will be accessed.
        method_name: String containing the name of the attribute.
        parameters: Dictionary containing the parameters used to call the requested function.
    Returns:
        If method_name is a function within instance its return value will be returned. 
        Else if method_name is a field withing instance its value will be returned.
        Else None will be returned.
    Raises:
        ValueError if parameters doesn't contain all the needed parameter function that is requiered to call the requested function.
    """
    # Check if the instance owns the requested attribute. If it doesn't return None. 
    if hasattr(instance, method_name):
        attribute_ = getattr(instance, method_name)
    else:
        attribute_ = None
    # If the requested attribute is a method, call it: 
    # Note that: callable(None) returns False.

    if(callable(attribute_)) :
        method_ = attribute_
        validated_params = validate_parameters(parameters, method_)
        returned_val = method_(**validated_params)
    # Else the attribute might actually be a field. Return it's value:
    else :
        if "value" in parameters:
            setattr(instance, method_name, parameters["value"])
        returned_val = getattr(instance, method_name)

    return returned_val

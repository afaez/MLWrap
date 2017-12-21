from importlib import import_module # used to dereference module names. see function: construct
import inspect
from inspect import signature # used to inspect function signature. see function: _validate_parameters


import pase.constants.error_msg as error # Contains error messages constants.


def _validate_parameters(given_param, callable_):
    """ validates the parameters from the given_param and returns a clean paramter dictionary.
    Parameters:
        given_param: Dictionary given to call the callable_
        callable_: Python callable object. Can be a function or a constructor.
    Returns: 
        A sanitized parameter dictionary that can be used to call the callable_.
    Raises:
        ValueError, if there is a parameter in callable's signature that is mandatory and given_param doesn't contain it.
    """
     # Now create a validated dictionary based on the signature from the method: 
    validated_dict = {}
    signature_ = signature(callable_)
    # iterate over every parameter:
    for param_key in signature_.parameters:
        if(param_key in given_param):
            # Copy parameters to the validated dictionary:
            validated_dict[param_key] = given_param[param_key]
        elif(signature_.parameters[param_key].default == inspect._empty): # No default is set.
            # The parameter wasn't sent by the client. 
            raise ValueError(error.const.parameter_is_mandatory.format(f"{param_key}"))

    return validated_dict
    
    
def construct(module_name, class_name, parameters):
    """ Dereferences a module by its module_name and dereferences a class from module by its class_name and calls constructs it using the given paramters.
    """ 
    try:
        # Import the requested module:
        module = import_module(module_name)
        # 
        clazz = getattr(module, class_name)
        if(not callable(clazz)):
            raise ValueError(error.const.cannot_construct_class_name.format(class_name, module_name))
        # Validate the parameters:
        validated_params = _validate_parameters(parameters, clazz)
        # Call the constructor:
        instance = clazz(**validated_params)
    except ModuleNotFoundError as e:
        print(f"{e}")
        raise ValueError(error.const.module_not_found.format(module_name))
    except AttributeError as e:
        print(f"{e}")
        raise e #ValueError(error.const.class_not_found_in_module.format( class_name, module_name))
    



    return instance

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
        validated_params = _validate_parameters(parameters, method_)
        returned_val = method_(**validated_dict)
    # Else the attribute might actually be a field. Return it's value:
    else :
        returned_val = attribute_

    return returned_val
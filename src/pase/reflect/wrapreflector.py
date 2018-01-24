from . import reflector
from pase import config
import logging


def construct(class_path_list, kwargs):
    """ Wrap the class construct into the wrapper constructor.
    """

    class_path_string = ".".join(class_path_list)
    wrap_path = config.lookup.get_wrapper(class_path_string)
    wrap_path_list = wrap_path.split(".")
    logging.debug(f"Wrapping {class_path_string} in {wrap_path}")

    # Get the wrapper module to call it
    try:
        wrapper_module = reflector.traverse_package(wrap_path_list)
    except ModuleNotFoundError as ex:
        raise ValueError(f"{ex}")

    # Get the class module that is being wrapped
    try:
        class_module = reflector.traverse_package(class_path_list)
    except ModuleNotFoundError as ex:
        raise ValueError(f"{ex}")
    # validate parameters
    validated_param = reflector.validate_parameters(kwargs, class_module)
    # create the wrapper instance
    wrapperinstance = wrapper_module(class_module, validated_param)
    logging.debug(f"Created instance {wrapperinstance}")
    # return the wrapper instance together with the fully qualified path name from the configuration.
    return wrapperinstance, config.lookup.fullname(class_path_string)

    
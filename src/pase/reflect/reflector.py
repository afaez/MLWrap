import importlib

def construct(module_name, class_name, parameter):
    try:
        module = importlib.import_module(module_name)
        clazz = getattr(module, clazz)
        instance = clazz(**parameter)
    except Exception as e:
        printf(f"{e}")
        raise e

    return instance

def call(instance, method_name, parameter):
    method = getattr(instance, method_name)
    returned_val = method(**parameter)
    return returned_val
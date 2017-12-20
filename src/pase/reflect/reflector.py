import importlib

def construct(module_name, class_name, parameter):
    try:
        module = importlib.import_module(module_name)
        clazz = getattr(module, class_name)
        instance = clazz(**parameter)
    except Exception as e:
        print(f"{e}")
        raise e

    return instance

def call(instance, method_name, parameter):
    method = getattr(instance, method_name)
    returned_val = method(**parameter)
    return returned_val
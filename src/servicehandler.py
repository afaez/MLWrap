from flask import Flask
from flask import request
from flask_api import status
import json
from pase import store as store
from pase import reflect as reflect
from pase.marshal import marshal as marshal, marshaldict
from pase import composition as composition
import pase.config as config
import pase.constants.error_msg as error
import jsonpickle.ext.numpy as jsonpickle_numpy
import logging

def create(class_path, body):
    # Check if requested class is in the configuration whitelist.
    if not config.whitelisted(class_path):
        return error.const.class_is_not_accessible.format(class_path), status.HTTP_405_METHOD_NOT_ALLOWED
    # Split the class_path into a list of paths.
    path_list = _split_packages(class_path)

    # If path list is empty or only contains one value, return error:
    if len(path_list) < 2:
        return error.const.no_package_was_sent, status.HTTP_400_BAD_REQUEST
    # Create the instance objects:
    try:
        instance, class_name = reflect.construct(path_list, body)
    except ValueError as ve:
        return f"{ve}", status.HTTP_400_BAD_REQUEST
    # Save the instance object and create a new id:
    id = store.save(class_name, instance)
    return_dict = {"id": id, "class": class_name}
    return_json = json.dumps(return_dict)
    return return_json, {'Content-Type': 'application/json'}

def copy_instance(class_path, id):
    # Copies this instance into another instance and returns the new id.
    try:
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)
    except ValueError as ve:
        return f"{ve}"

    # Save the instance object as a new instance and create a new id:
    new_id = store.save(class_path, instance)
    return_dict = {"id": new_id, "class": class_path}
    return_json = json.dumps(return_dict)
    return return_json, {'Content-Type': 'application/json'}

def copy_call_method(class_path, id, method_name, jsondict):
    """ Calls method and saves the return value as a new instance. Returns classname and id of the saved return value.
    """
    try:
        return_value = _call_method(class_path, id, method_name, jsondict, True)
    except Exception as ex:
        return f"{ex}", status.HTTP_400_BAD_REQUEST

    # Save the return object as a new instance and create a new id:
    class_name = reflect.fullname(return_value)
    new_id = store.save(class_name, return_value)
    return_dict = {"id": new_id, "class": class_name}
    return_json = json.dumps(return_dict)
    return return_json, {'Content-Type': 'application/json'}

def call_method(class_path, id, method_name, jsondict, save = True):
    try:
        return_value = _call_method(class_path, id, method_name, jsondict, save)
    except Exception as ex:
        return f"{ex}", status.HTTP_400_BAD_REQUEST

    # Parse the output to json.
    return_json = marshal(return_value)

    return return_json, {'Content-Type': 'application/json'}

def _call_method(class_path, id, method_name, params, save = False):
    """ Handles calling the method. 
    """
    # Executes the method call 

    # Recover the instance from the memory:
    instance = store.restore(class_path, id)


    # Call the requested function or attribute:
    return_value = reflect.call(instance, method_name, params)
    
    # Change the state of the instance if HTTP method is PUT.
    # (POST guarantees that the state doesn't change.)
    if save:
        store.save(class_path, instance, id)
        
    return return_value

def execute_composition(choreo):
    """ Executes the given choreo
    """
    return_messages = []
    variables = {}
    # processes operation
    for operation in choreo:
        fieldname = operation.leftside 
        variables[fieldname] = None
        return_message = {"op" : f"{operation} < {operation.args} \n"}
        return_messages.append(return_message)
        for argname in operation.args:
            argument = operation.args[argname]
            try:
                if  argument in variables:
                    operation.args[argname] = variables[argument]
            except TypeError:
                pass


        instance = None
        if operation.clazz in variables:
            instance = variables[operation.clazz]
            try:
                instance = reflect.call(instance, operation.func, operation.args)
                return_message["msg"] = f"The Method {operation.func} from instance {instance} with args: {operation.args} called."
                return_message["status"] = "success"
            except ValueError as ve:
                return_message["msg"] = f"{ve}"
                return_message["status"] = "error"

        else:
            path_list = _split_packages(operation.clazz)
            if  "__construct" != operation.func:
                path_list.append(operation.func)
            try:
                instance, class_name = reflect.construct(path_list, operation.args)
                return_message["msg"] = f"Instance {instance} with type {class_name} created."
                return_message["status"] = "success"
            except ValueError as ve:
                return_message["msg"] = f"{ve}"
                return_message["status"] = "error"

        variables[fieldname] = instance
    logging.debug("Execution logs: \n" + json.dumps(return_messages, sort_keys=True, \
        indent=4, separators=(',', ': ')))
    return_variables = {}
    for return_name in choreo.return_list:

        if return_name in choreo.store_list:
            continue # The id of this will be returned. see below.
        
        if  return_name in variables:
            instance = variables[return_name]
        else:
            instance = None
        return_variables[return_name] = instance

    for store_name in choreo.store_list:
        if  store_name in variables:
            instance = variables[store_name]
            class_name = reflect.fullname(instance)
            id = store.save(class_name, instance)
            return_variables[store_name] = {"id": id, "class": class_name}
        else:
            return_variables[store_name] = None
    
    return marshaldict(return_variables)



def _split_packages(class_path):
    """ Splits the class_path by the '.' character. e.g.: _split_packages("package_name.module_name.Class_name") will return the list: ["package_name", "module_name", "Class_name"]
    """
    return class_path.split(".")

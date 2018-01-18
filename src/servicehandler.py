from flask import Flask
from flask import request
from flask_api import status
import json
from pase import store as store
from pase import reflect as reflect
from pase.marshal import marshal as marshal
from pase import composition as composition
import pase.config as config
import pase.constants.error_msg as error
import jsonpickle.ext.numpy as jsonpickle_numpy


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


def _split_packages(class_path):
    """ Splits the class_path by the '.' character. e.g.: _split_packages("package_name.module_name.Class_name") will return the list: ["package_name", "module_name", "Class_name"]
    """
    return class_path.split(".")
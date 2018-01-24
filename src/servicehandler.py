from flask import Flask
from flask import request
from flask_api import status
import json
from pase import store 
from pase import reflect 
from pase.marshal import marshal, marshaldict
from pase import composition 
from pase import config
import pase.constants.error_msg as error
import jsonpickle.ext.numpy as jsonpickle_numpy
import logging
import re

def create(class_path, body):
    # Check if requested class is in the configuration whitelist.
    if not config.lookup.class_known(class_path):
        return error.const.class_is_not_accessible.format(class_path), status.HTTP_405_METHOD_NOT_ALLOWED
    
    # Split the class_path into a list of paths.
    path_list = _split_packages(class_path)

    # If path list is empty or only contains one value, return error:
    if len(path_list) < 2:
        return error.const.no_package_was_sent, status.HTTP_400_BAD_REQUEST
    # Create the instance objects:
    try:
        logging.debug(f"Creat called: \n{path_list}\n{body}")
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


def call_method(class_path, id, method_name, jsondict, copy=False):
    """ Calls method and saves the return value as a new instance. 
    If copy is True, returns classname and id of the saved return value.
    Else it returns the marshalled return value.
    """
    try:
        return_value = _call_method(class_path, id, method_name, jsondict)
    except Exception as ex: # catch all exception
        logging.error(ex, exc_info=True)
        return f"{ex}", status.HTTP_400_BAD_REQUEST
    if copy:
        # Save the return object as a new instance and create a new id:
        class_name = reflect.fullname(return_value)
        new_id = store.save(class_name, return_value)
        return_dict = {"id": new_id, "class": class_name}
        return_json = json.dumps(return_dict)
    else:
        # Parse the output to json.
        return_json = marshal(return_value)

    return return_json, {'Content-Type': 'application/json'}

def _call_method(class_path, id, method_name, params):
    """ Handles the logic behind calling the method. 
    """
    # Executes the method call 

    # Recover the instance from the memory:
    instance = store.restore(class_path, id)


    # Call the requested function or attribute:
    return_value = reflect.call(instance, method_name, params)
    
    # Change the state of the instance if HTTP method is PUT.
    # (POST guarantees that the state doesn't change.)
    store.save(class_path, instance, id)
        
    return return_value

def execute_composition(choreo):
    """ Executes the given choreo
    """
    return_messages = []
    variables = {}

    # check if currentindex points to the new one.
    if len(choreo.operation_list)<=choreo.currentindex:
        logging.debug(f"body_string has less operations than the currentindex={choreo.currentindex} points to: {choreo}")
        return "nothing to execute", status.HTTP_400_BAD_REQUEST

    # 


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
                logging.error(ve, exc_info=True)
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

def setuplogging():
    """ Takes care of setting up the logging. If this method isn't used, 'WARNING' logs will be printed to stdout. 
    """
    import datetime
    now  = datetime.datetime.now()
    import pathlib
    # directory where the logs are collected
    directory = '../logs'
    # create log directory if it doesn't exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True) 
    # logfile  path definition
    logfilepath = directory + "/pase_{}.log".format(now.strftime("%Y-%m-%d_%H-%M-%S"))
    print("logging in " + logfilepath)
    # logs will be written to the ^ upper ^ logfile.
    # TODO get logging lvl from configuration
    logging.basicConfig(filename=logfilepath,level=logging.DEBUG) 

def bodystring_to_bodydict(body_string):
    """ Creates a dict object from a string. 
    This method conforms to the implementation of JASE, so the JASE-client can communicate with the server.
    If successfull it returns a dictionary with the following fields:
        - "execute" : Contains a string which represents the code from the composition to be executed
        - "input" : Contains another dict object.
    """
    if not body_string: 
        # the given string is null or empty
        raise ValueError("None or empty string was given.")

    body_string = body_string.strip()
    request_dictionary = dict() # this will be returned.
    pairs = body_string.split("&") # split by '&'
    # create parameter object
    parameters = {}
    for pair in pairs:
        # split only returns on array of size two: "A=B=C" -> ["A", "B=C"]
        parameter = pair.split("=", 1) 
        if len(parameter) < 2:
            continue
        key = parameter[0]
        value = parameter[1]
        if key in parameters:
            # key was already found. add to the list in the dictionary:
            list_ = list(parameter[key])
            list_.append(value)
            parameters[key] = list_
        else:
            # First time adding
            parameters[key] = value

    # Extract coreography and index
    if "coreography" in parameters:
        choreography_string = parameters["coreography"]
        request_dictionary["execute"] = choreography_string
        logging.debug(f"choreo: {choreography_string}")

    if "currentindex" not in parameters:
        request_dictionary["currentindex"] = 0
    else:
        request_dictionary["currentindex"] = parameters["currentindex"]

    # json deserialise inputs and put them by their indexes into 'inputs' dictionary
    inputs = {"arglist":[]}
    for key in parameters:
        if not key.startswith("inputs"):
            # this is not an input
            continue

        # Extract index from brackets. e.g.: inputName =  "inputs[i1]" -> index = "i1"
        index = find_between(key, '[', ']')
        input_stringvalue = str(parameters[key])
        input_object = json.loads(input_stringvalue)

        if not isinstance(input_object, dict) or "type" not in input_object:
            # the json input doesn't have a type field.
            raise ValueError(f"No type field in inputs[{index}]={input_stringvalue}")
        if not config.lookup.check_type(input_object["type"]):
            # The given type isn't known by the marshalling system.
            type_ = input_object["type"]
            raise ValueError(f"The given type = {type_} isn't known by the system.")
        if re.match("^i[0-9]+$", index): 
            # if the index matches the pattern it is a positional argument. like i1, i2...
            # extract index: index = i10 -> index = 10
            index = int(index[1:]) 
            # insert value in the arglist array in position=index:
            inputs["arglist"][index] = input_object
        else:
            # it is a keyword argument
            inputs[index] = input_object

    request_dictionary["input"] = inputs

    return request_dictionary

def _split_packages(class_path):
    """ Splits the class_path by the '.' character. e.g.: _split_packages("package_name.module_name.Class_name") will return the list: ["package_name", "module_name", "Class_name"]
    """
    return class_path.split(".")

def find_between(s, first, last):
    """ Extracts the substring in between two delimiters.
    """
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
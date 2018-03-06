from flask import Flask
from flask import request
from flask_api import status
import json
from pase.servicehandle import ServiceHandle
from pase.pase_dataobject import PASEDataObject
from pase import store 
from pase import reflect 
from pase.marshal import marshal, marshaldict, unmarshal
from pase import composition 
from pase import config
import pase.constants.error_msg as error
import jsonpickle.ext.numpy as jsonpickle_numpy
import logging 
import re # regular expression used in bodystring_to_bodydict()
import traceback # for logging stacktraces in compsition execution method
import compositionclient
import traceback
import time


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
    try:
        id = store.save(class_name, instance)
        service = ServiceHandle.local_service(class_name, id, instance)
        return service
        
    except Exception as ex:
        # some internal error occurred.
        return_msg = str(ex)
        return return_msg, status.HTTP_500_INTERNAL_SERVER_ERROR

def copy_instance(class_path, id):
    # Copies this instance into another instance and returns the new id.
    try:
    starttime = time.time()
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)
    except ValueError as ve:
        return f"{ve}"

    # Save the instance object as a new instance and create a new id:
    new_id = store.save(class_path, instance)
    service = ServiceHandle.local_service(class_path, new_id, instance)
    return service

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
        # TODO

    return return_value

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

    # check if currentindex is in range.
    if len(choreo.operation_list)<=choreo.currentindex:
        logging.error(f"body_string has less operations than the currentindex={choreo.currentindex} points to: {choreo}")
        return "nothing to execute", status.HTTP_400_BAD_REQUEST
    
    
    # variables are a copy of input_dict
    variables = dict(choreo.input_dict)

    logging.debug("variables: " + str(variables.keys()))
    operatingindex = -1 # the index of the current executing operation.
    # processes operation
    for operation in choreo:
        
        #logging.debug(f"Vars dict: {variables}")

        # increase operatingindex until it reaches currentindex.
        operatingindex +=  1
        if operatingindex < choreo.currentindex:
            continue

        # don't go over maxindex. (maxindex'th operation itself is not included)
        if  choreo.maxindex != -1 and operatingindex >= choreo.maxindex:
            break

        # Execute operation

        fieldname = operation.leftside # fieldname the result is assigned to
        # fill positional arguments
        referenced_argument = operation.args["$arglist$"]
        filled_arguments = []
        for argument in referenced_argument:
            if  argument in variables:
                    filled_arguments.append(unmarshal(variables[argument]))
            else:
                    filled_arguments.append(argument)
        # replace the list with the filled list
        operation.args["$arglist$"] = filled_arguments

        # fill keyword arguments
        for argname in operation.args:
            argument = operation.args[argname]
            try:
                if  argument in variables:
                    operation.args[argname] = unmarshal(variables[argument])
            except TypeError:
                pass
        # print(f"executing op\"{operation}\" at index={operatingindex} with inputs={str(operation.args)[0:100]}")
        logging.debug(f"executing op\"{operation}\" at index={operatingindex}") # with inputs={operation.args}")
        starttime = time.time()
        error = None
        instance = None
        # execute rightside function
        try:
            executed = False
            if operation.clazz in variables:
                # method call
                instance = variables[operation.clazz]
                if isinstance(instance, ServiceHandle) and not instance.is_remote():
                    serviceInstance = instance.service
                    returnvalue = reflect.call(serviceInstance, operation.func, operation.args)
                    variables[fieldname] = returnvalue
                    executed = True

            elif config.lookup.class_known(operation.clazz + "." + operation.func):
                # construction
                path_list = _split_packages(operation.clazz)
                if  "__construct" != operation.func:
                    path_list.append(operation.func)
                instance, classpath = reflect.construct(path_list, operation.args)
                service_id = store.save(classpath, instance)
                service = ServiceHandle.local_service(classpath, service_id, instance)
                variables[fieldname] = service
                executed = True
            if not executed:
                # forward
                # If the class that has to be constructed isn't known/allowed by this server, call the next service:
                compositionclient.forwardoperation(variables, operatingindex, choreo)
            endtime = time.time()

            logging.debug("Operation execution done in {:9.3f} seconds.".format(endtime - starttime))
        except Exception as ex:
            logging.error(ex, exc_info=True)
            error = traceback.format_exc()
            break
        
        
        # logging.debug(f"state after op:{variables}")

        # END OF FOR LOOP

    # write all the local servicehandlers to disk:
    for fieldname in variables:
        handle = variables[fieldname]
        if not isinstance(handle, ServiceHandle):
            continue
        if not handle.is_remote():
            store.save(handle.classpath, handle.service, handle.id)

    if error is not None:
        returnbody = {"error": error}
        return returnbody

    return_variables = {}

    for return_name in choreo.return_list:      
        if  return_name in variables:
            instance = variables[return_name]
        else:
            instance = None
        return_variables[return_name] = instance

    # print("serializing " + str(return_variables)) 
    returnbody = composition.Choreography.todict(variables=return_variables)


    # print("Returning : " + str(returnbody)[0:3000])
    return returnbody

def getlogs():
    import os.path
    import os
    directory_in_str = '../logs'
    if not os.path.isdir(directory_in_str):
        return "Error: no log folder found."

    directory = os.fsencode(directory_in_str)
    allcontent = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        logfilepath = os.path.join(directory_in_str, filename)
        with open(logfilepath, 'r') as logfile:
            try:
                contentlist = logfile.readlines()
            except:
                contentlist = ["Couln't read the log file: {}".format(logfilepath)]
            allcontent[filename] = contentlist
    return allcontent



    

def setuplogging(id = 0):
    """ Takes care of setting up the logging. If this method isn't used, 'WARNING' logs will be printed to stdout. 
    """
    import pathlib
    # directory where the logs are collected
    directory = '../logs'
    # create log directory if it doesn't exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True) 
    # logfile  path definition
    # logfilename = "/pase_{}.log".format(now.strftime("%Y-%m-%d_%H-%M-%S"))
    logfilename = "/pase_{}.log"
    logfilepath = directory + logfilename.format(id)

    # logs will be written to the ^ upper ^ logfile.
    # TODO get logging lvl from configuration

    logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=logfilepath,
                    filemode='w')

    print("logging into " + logfilepath)

def bodystring_to_bodydict(body_string):
    """ Creates a dictionary object from a string. 
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

    if "currentindex" in parameters:
        request_dictionary["currentindex"] = parameters["currentindex"]
    
    if "maxindex" in parameters:
        request_dictionary["maxindex"] = parameters["maxindex"]

    # json deserialise inputs and put them by their indexes into 'inputs' dictionary
    inputs = {"$arglist$":[]}
    for key in parameters:
        if not key.startswith("inputs"):
            # this is not an input
            continue

        # Extract index from brackets. e.g.: inputName =  "inputs[i1]" -> index = "i1"
        index = find_between(key, '[', ']')
        input_stringvalue = str(parameters[key])
        input_object = json.loads(input_stringvalue)

        # Currently the type isn't checked by the system.
        # if not isinstance(input_object, dict) or "type" not in input_object:
        #     # the json input doesn't have a type field.
        #     raise ValueError(f"No type field in inputs[{index}]={input_stringvalue}")
        # if not config.lookup.check_type(input_object["type"]):
        #     # The given type isn't known by the marshalling system.
        #     type_ = input_object["type"]
        #     raise ValueError(f"The given type = {type_} isn't known by the system.")
        
        # it is a keyword argument
        inputs[index] = input_object

        # Extract indexes into $arglist$ for single execution
        if re.match("^i[0-9]+$", index): 
            # if the index matches the pattern it is a positional argument. like i1, i2...
            # extract index: index = i10 -> index = 10
            index = int(index[1:]) 
            # insert value in the $arglist$ array in position=index:
            while len(inputs["$arglist$"]) <= index:
                # List isn't big enough
                inputs["$arglist$"].append(None)
            inputs["$arglist$"][index] = input_object
        

    request_dictionary["input"] = inputs

    if ("execute" in request_dictionary):
        # This is a choreography. 
        return request_dictionary
    else:
        # This is a service call consisting of one operation. Return the inputs only.
        return inputs

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
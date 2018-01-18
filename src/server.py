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
application = Flask(__name__)
jsonpickle_numpy.register_handlers()

import servicehandler


@application.route("/<class_path>", methods=['POST'])
def create(class_path):
    # Request body contains constructor parameters
    jsondict = parse_jsonbody()
    # Delegate call to the servicehandler
    return servicehandler.create(class_path, jsondict)

@application.route("/<class_path>/copy/<id>", methods=['GET'])
def copy_instance(class_path, id):
    return servicehandler.copy_instance(class_path, id)

@application.route("/<class_path>/copy/<id>/<method_name>", methods=['POST', 'GET'])
def copy_call_method(class_path, id, method_name):
    jsondict = parse_jsonbody()
    return servicehandler.copy_call_method(class_path, id, method_name, jsondict)

@application.route("/<class_path>/<id>/<method_name>", methods=['POST', 'GET'])
def call_method(class_path, id, method_name, save = True):
    #print(f"Call method received: {class_path}:{id}:{method_name}")
    if request.method == "GET":
        save = False
    jsondict = parse_jsonbody()
    return_val1, return_val2 = servicehandler.call_method(class_path, id, method_name, jsondict, save)
    #print(f"returning: \n {return_val1} \n {return_val2}")
    return return_val1

@application.route("/<class_path>/<id>", methods=['GET'])
def retrieve_state(class_path, id):
    """ Returns the json serialized state of the object of the given id.
    """
    try:
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)

    except ValueError as ve:
        return f"{ve}"

    return marshal(instance), {'Content-Type': 'application/json'}

@application.route("/composition", methods=['POST'])
def composition_request():
    # Request body contains constructor parameters
    body = request.get_json()
    choreo = composition.Choreography.fromdict(body)
    return_messages = []

    variables = {}
    # processes operation
    for operation in choreo:
        fieldname = operation.leftside 
        variables[fieldname] = None
        for argname in operation.args:
            argument = operation.args[argname]
            try:
                if  argument in variables:
                    operation.args[argname] = variables[argument]
            except TypeError:
                pass

        return_message = {"op" : f"{operation} < {operation.args} \n"}
        return_messages.append(return_message)

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
            path_list = servicehandler._split_packages(operation.clazz)
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

    return_dict = {"log" : return_messages}
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

    return_dict["return"] = return_variables
    return marshal(return_dict)

def parse_jsonbody():
    """ Parses and returns the json body from the http request. 
    Returns an empty dictionary in case the http request body can't be parsed as a json string.
    """
    # force means that mimetypes are ignored. (So there is no need for 'application/json' in the header.)
    # silent means that in case of a fail it won't raise an exception.
    body = request.get_json(force = True, silent = True) 
    if body is None:
        body = {}
    return body


if __name__ == '__main__':
    # Retrieve the command line argument to use as a port number.
    port_ = 5000 
    try:
        import sys
        port_ = int(sys.argv[1]) # port is the first command line argument.
    except:
        pass
    # Run the server
    application.run(host='localhost', port=port_, debug = config.debugging())


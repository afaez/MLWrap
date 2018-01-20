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
    return servicehandler.execute_composition(choreo)

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


from flask import Flask
from flask import request
from flask_api import status
import json
from pase import store as store
from pase import reflect as reflect
from pase.marshal import marshal as marshal
from pase import composition as composition
import pase.constants.error_msg as error
import jsonpickle.ext.numpy as jsonpickle_numpy
import servicehandler
import logging

#setup logging.
servicehandler.setuplogging()

# register handlers for jacksonpickle to be used with numpy.
jsonpickle_numpy.register_handlers()

# flask application 
application = Flask(__name__)


@application.route("/<class_path>", methods=['POST'])
def create(class_path):
    # Request body contains constructor parameters
    jsondict, _ = parse_jsonbody()
    # Delegate call to the servicehandler
    return servicehandler.create(class_path, jsondict)

@application.route("/<class_path>/copy/<id>", methods=['GET'])
def copy_instance(class_path, id):
    return servicehandler.copy_instance(class_path, id)

@application.route("/<class_path>/copy/<id>/<method_name>", methods=['POST', 'GET'])
def copy_call_method(class_path, id, method_name):
    jsondict, _ = parse_jsonbody()
    return servicehandler.call_method(class_path, id, method_name, jsondict, copy=True)

@application.route("/<class_path>/<id>/<method_name>", methods=['POST', 'GET'])
def call_method(class_path, id, method_name):
    if request.method == "GET":
        save = False
    jsondict, _ = parse_jsonbody()
    print(f"Call method received: {class_path}:{id}:{method_name} < {jsondict}")
    return_val1, return_val2 = servicehandler.call_method(class_path, id, method_name, jsondict)
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

@application.route("/<class_path>/<op>", methods=['POST'])
def composition_request(class_path, op):
    # Parse body to json. json_content is true, if content-type is set to 'application/json'.
    body, json_content = parse_jsonbody()
    if json_content:
        # Header has 'application/json', so it can't be from a Jase client.
        print(body["input"])
        return servicehandler.create(class_path+"."+op, body["input"])
    else:
        choreo = composition.Choreography.fromdict(body)
        return servicehandler.execute_composition(choreo)

# @application.route("/composition", methods=['POST'])
# def composition_request():
#     # Request body contains constructor parameters
#     body = request.get_json()
#     choreo = composition.Choreography.fromdict(body)
#     return servicehandler.execute_composition(choreo)

def parse_jsonbody():
    """ Parses and returns the json body from the http request. 
    Returns an empty dictionary in case the http request body can't be parsed as a json string.
    """
    #print(request.headers.get('content-type'))
    if 'application/json' in request.headers.get('content-type').lower() :
        # force means that mimetypes are ignored. 
        # (So there is no need for 'application/json' in the header.)
        # silent means that in case of a fail it won't raise an exception.
        body = request.get_json(force = True, silent = True) 
        #logging.debug(f"read body{body}")
        if body is None:
            body = {} # put empty dict in case of an invalid syntax.
        jsoncontent = True
    else:
        # read inputstream directly and decode it to string:
        string_body = readhttpstream()
        body = servicehandler.bodystring_to_bodydict(string_body)
        jsoncontent = False
        
    return body, jsoncontent


def readhttpstream():
    """ Reads the bytes in the http stream and returns the decoded string.
    """
    length = request.headers.get("Content-Length", type = int)
    data = bytearray()
    chunk_size = length
    while True:
        # Read chunk from the stream
        chunk = request.stream.read(chunk_size)
        if len(chunk) != 0:
            # put data into array
            data.extend(chunk)
        else :
            # chunk is empty
            break
    #print("---> Sream length: \n", len(data)) 
    # Decode data using utf-8 and replace.
    decodeddata = data.decode("utf-8", "replace")
    #print("---> Sream: \n", decodeddata[:])
    return decodeddata


if __name__ == '__main__':
    # Retrieve the command line argument to use as a port number.
    port_ = 5000 
    try:
        import sys
        port_ = int(sys.argv[1]) # port is the first command line argument.
    except:
        pass
    # Run the server
    import pase.config
    application.run(host='localhost', port=port_, debug = pase.config.debugging())


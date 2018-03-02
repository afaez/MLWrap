from flask import Flask
from flask import request
from flask_api import status
import json
import htmlparser
from pase import store as store
from pase import reflect as reflect
from pase.marshal import unmarshal
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

@application.route("/logs/<range>", methods=['GET'])
def read_logs(range):

    msg = servicehandler.getlogs(int(range))
    return htmlparser.parse(msg)

@application.route("/<class_path>/__construct", methods=['POST'])
@application.route("/<class_path>", methods=['POST'])
def create(class_path):
    inputs = parse_inputs()
    # Request body contains constructor parameters
    servicehandle = servicehandler.create(class_path, inputs)

    returnbody = create_body({"out":servicehandle})
    return returnbody, {'Content-Type': 'application/json'}

@application.route("/<class_path>/copy/<id>", methods=['GET'])
def copy_instance(class_path, id):
    servicehandle = servicehandler.copy_instance(class_path, id)

    returnbody = create_body({"out":servicehandle})
    return returnbody, {'Content-Type': 'application/json'}

@application.route("/<class_path>/copy/<id>/<method_name>", methods=['POST', 'GET'])
def copy_call_method(class_path, id, method_name):
    inputs = parse_inputs()
    vars = servicehandler.call_method(class_path, id, method_name, inputs, copy=True)
    
    returnbody = create_body({"out":vars})
    return returnbody, {'Content-Type': 'application/json'}

@application.route("/<class_path>/<id>/<method_name>", methods=['POST', 'GET'])
def call_method(class_path, id, method_name):
    if request.method == "GET":
        save = False
    inputs = parse_inputs()
    logging.debug(f"Call method received: {class_path}:{id}:{method_name} < {inputs}")
    return_val = servicehandler.call_method(class_path, id, method_name, inputs)

    returnbody = create_body({"out":return_val})
    return returnbody, {'Content-Type': 'application/json'}


@application.route("/choreography", methods=['POST'])
def composition_request():
    # Parse body to json. json_content is true, if content-type is set to 'application/json'.
    body = parse_jsonbody()
    choreo = composition.Choreography.fromdict(body)

    returnbody = servicehandler.execute_composition(choreo)
    if "error" in returnbody:
        return returnbody["error"], 400
    else:
        return json.dumps(returnbody)

def create_body(variables):
    """ Creates the return body of the given variabeles
    """
    if not isinstance(variables, dict):
        raise ValueError("Can't parse to body: " + variables)
    
    returnbody = composition.Choreography.todict(variables=variables)
    return_string = json.dumps(returnbody)
    return return_string


def parse_inputs():
    """ Parses body of the request and extracts the inputs and returns the deserialisation.
    """
    jsonBody = parse_jsonbody()
    inputs = composition.Choreography.fromdict(jsonBody, translate_positional_args=False).input_dict
    for argname in inputs:
        inputs[argname] = unmarshal(inputs[argname]) # unwrap the values from PASEDataobjects
    return inputs


def parse_jsonbody():
    """ Parses and returns the json body from the http request. 
    """
    # read inputstream directly and decode it to string:
    string_body = readhttpstream()
    body = json.loads(string_body)
    return body


def readhttpstream():
    """ Reads the bytes in the http stream and returns the decoded string.
    """
    request.environ['wsgi.input_terminated'] = True
    data = bytearray()
    chunk_size = 4096
    while True:
        # Read chunk from the stream
        chunk = request.stream.read(chunk_size)
        if len(chunk) != 0:
            # put data into array
            data.extend(chunk)
        else :
            # chunk is empty
            break
    logging.debug("---> Sream length: %(a)d", {'a':len(data)})
    # Decode data using utf-8 and replace.
    decodeddata = data.decode("utf-8", "replace")
    # logging.debug(f"---> Sream content: {decodeddata}")
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


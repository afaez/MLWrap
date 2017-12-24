from flask import Flask
from flask import request
from flask_api import status
import json
import jsonpickle
from pase import store as store
from pase import reflect as reflect
import pase.params.config as config
import pase.constants.error_msg as error

app = Flask(__name__)
import jsonpickle.ext.numpy as jsonpickle_numpy

jsonpickle_numpy.register_handlers()


@app.route("/<class_path>", methods=['POST'])
def create(class_path):
    # Check if requested class is in the configuration whitelist.
    if not config.is_in_whitelist(class_path):
        return error.const.class_is_not_accessible.format(class_path), status.HTTP_405_METHOD_NOT_ALLOWED
        

    # Split the class_path into a list of paths.
    path_list = _split_packages(class_path)
    # Request body contains constructor parameters
    body = request.get_json()

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
    return return_json


@app.route("/<class_path>/safe/<id>/<method_name>", methods=['POST', 'PUT', 'GET'])
def call_method_(class_path, id, method_name):
    # This route guarantees that the state of the object doesn't change.
    return call_method(class_path, id, method_name, save = False)

@app.route("/<class_path>/<id>/<method_name>", methods=['POST', 'PUT', 'GET'])
def call_method(class_path, id, method_name, save = True):
    # Parse the parameters from the body:
    if request.method != 'GET'  :
        params = request.get_json()
    else: 
        params = {}
        save = False # Get doesn't change server state.
    try:
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)

        # Call the requested function or attribute:
        return_value = reflect.call(instance, method_name, params)
    except Exception as ex:
        return f"{ex}", status.HTTP_400_BAD_REQUEST

    # Change the state of the instance if HTTP method is PUT.
    # (POST guarantees that the state doesn't change.)
    if save:
        store.save(class_path, instance, id)

    # Parse the output to json.
    return_json = _serialize_output(return_value)

    return return_json


@app.route("/<class_path>/<id>", methods=['GET'])
def retrieve_state(class_path, id):
    """ Returns the json serialized state of the object of the given id.
    """
    try:
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)

    except ValueError as ve:
        return f"{ve}"

    return _serialize_output(instance)


def _split_packages(class_path):
    """ Splits the class_path by the '.' character. e.g.: _split_packages("package_name.module_name.Class_name") will return the list: ["package_name", "module_name", "Class_name"]
    """
    return class_path.split(".")

def _serialize_output(output):
    """ Returns the json serialized output of function calls which is sent back to clients:
    """
    # TODO: How should we return the return value?
    try:
        # If it is json serializable, do it:
        return_json = json.dumps(output)
    except TypeError:
        # Else just parse it to string and return its string represtation. 
        return_json = jsonpickle.dumps(output, unpicklable=False)
    return return_json


app.run(debug=config.DEBUGGING)

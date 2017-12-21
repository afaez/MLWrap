from flask import Flask
from flask import request
import json
from pase import store as store
from pase import reflect as reflect
import pase.params.config as config
import pase.constants.error_msg as error

app = Flask(__name__)
import jsonpickle.ext.numpy as jsonpickle_numpy

jsonpickle_numpy.register_handlers()


@app.route("/<class_path>", methods=['POST'])
def create(class_path):
    if not config.is_in_whitelist(class_path):
        return error.const.class_is_not_accessible.format(class_path)
    package, class_name = _get_package_and_class_name(class_path)
    # Request body contains constructor parameters
    body = request.get_json()
    # Create the instance objects:
    try:
        instance = reflect.construct(package, class_name, body)
    except ValueError as ve:
        return f"{ve}"
    # Save the instance object and create a new id:
    id = store.save(class_path, instance)
    return_dict = {"id": id}
    return_json = json.dumps(return_dict)
    return return_json


@app.route("/<class_path>/<id>/<method_name>", methods=['POST', 'PUT'])
def call_method(class_path, id, method_name):
    # Parse the parameters from the body:
    body = request.get_json()
    try:
        # Recover the instance from the memory:
        instance = store.restore(class_path, id)
    except ValueError as ve:
        return f"{ve}"

    # Call the requested function or attribute:
    try:
        return_val = reflect.call(instance, method_name, body)
    except ValueError as ve:
        return f"{ve}"

    # Change the state of the instance if HTTP method is PUT. (POST guarantees that the state doesn't change.)
    if request.method == 'PUT':
        store.save(class_path, instance, id)
    
    # Parse the output to json.
    # TODO: How should we return the return value?
    try:
        # If it is json serializable, do it:
        return_dict = {"return": return_val}
        return_json = json.dumps(return_dict)
    except TypeError:
        # Else just parse it to string and return its string represtation. 
        return_dict = {"return": f"{return_val}"}
        return_json = json.dumps(return_dict)

    return return_json


@app.route("/<class_path>/<id>", methods=['GET'])
def retrieve_state(class_path, id):
    """ Returns the json serialized state of the object of the given id.
    """
    try:
        # Recover the instance from the memory:
        json_string = store.restore_state(class_path, id)
    except ValueError as ve:
        return f"{ve}"
    
    return json_string


def _get_package_and_class_name(class_path):
    """ Splits the class_path into package_name and class_name. e.g.: "package_name.module_name.Class_name" will return "package_name.module_name" and "Class_name"
    """
    class_name = class_path.split(".")[-1]
    package = class_path[:-len(class_name) - 1]
    return package, class_name



app.run(debug=True)

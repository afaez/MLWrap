from flask import Flask
from flask import request
import json
from pase import store as store
from pase import reflect as reflect
app = Flask(__name__)
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()

@app.route("/<class_path>", methods=['POST'])
def create(class_path):
    class_name = class_path.split(".")[-1]
    package = class_path[:-len(class_name) - 1]
    body = request.get_json()
    instance = reflect.construct(package, class_name, body)
    id = store.save(class_path, instance)
    return_dict = {"id" : id}
    return_json = json.dumps(return_dict)
    return return_json


@app.route("/<class_path>/<id>/<method_name>", methods= ['POST', 'GET'])
def call_method(class_path, id, method_name):
    # Split the class name from the package.module name:
    class_name = class_path.split(".")[-1]
    package = class_path[:-len(class_name) - 1]
    # Parse the parameters from the body:
    body = request.get_json()

    # Recover the instance from the memory:
    instance = store.restore(class_path, id)

    # Call the requested function or attribute:
    return_val = reflect.call(instance, method_name, body)

    # Change the state of the instance if HTTP method is POST. (GET guarantees that the state doesn't change.)
    if request.method == 'POST':
        store.save(class_path,instance, id)

    return_dict = {"return" : return_val}
    return_json = f"{return_dict}"
    return return_json


app.run(debug=True)

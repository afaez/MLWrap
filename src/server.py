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


@app.route("/<class_path>/<id>/<method_name>", methods= ['POST'])
def call_method(class_path, id, method_name):
    class_name = class_path.split(".")[-1]
    package = class_path[:-len(class_name) - 1]
    body = request.get_json()
    instance = store.restore(class_path, id)
    return_val = reflect.call(instance, method_name, body)
    store.save(class_path,instance, id)
    return_dict = {"return" : return_val}
    return_json = f"{return_dict}"
    return return_json


app.run(debug=True)

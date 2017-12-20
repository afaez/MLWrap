from flask import Flask
from flask import request
import json

app = Flask(__name__)


@app.route("/<class_path>", methods=['POST'])
def create(class_path):
    class_name = class_path.split(".")[-1]
    package = class_path[:-len(class_name) - 1]
    body = request.get_json()
    return package + " " + class_name + str(body)


@app.route("/<class_name>/<id>/<method_name>")
def call_method(class_name, id, method_name):
    return "ok"


app.run(debug=True)

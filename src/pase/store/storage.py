# This module 
import os
import uuid 
import pase.constants.error_msg as error
import jsonpickle

def save(class_name, instance, id = None):

    # Boundary checks.
    if(not isinstance(class_name, str) ):
        raise ValueError(error.const.not_a_string.format("class_name"))
    if(instance is None)
        raise ValueError(error.const.is_null.format("instance"))

    # The path to the instance.
    # Instances are stored in a subfolder named after the type's name.
    path = class_name + "/"

    # Create folder if it doesnt exist.
    os.makedirs(path, exist_ok = True)

    # Generate id if id is not given.
    while id is None:
        id = uuid.uuid4().hex[:10].upper()
        if(os.path.isfile(path + id)):
            id = None

    # Finish the path.
    path = path + id

    # Serialize the object:
    jsonstring = jsonpickle.encode(instance)

    # file pointer
    file = open(path, )
# This module 
import os
import uuid 
import pase.constants.error_msg as error
# import jsonpickle
import pickle
import time
import logging

def _topath(class_name):
    return  "../data/" + class_name

def _tofilepath(class_name, id):
    return "../data/" + class_name + "/" + id

def _do_error_checks(class_name, id = None):
    """ Private function that checks if parameters are chosen without errors.
    """
     # Boundary checks.
    if(not isinstance(class_name, str) ):
        raise ValueError(error.const.not_a_string.format(f"class_name={class_name}"))

    # The path to the instance.
    path = _topath(class_name)
    # Create folder if it doesnt exist.
    os.makedirs(path, exist_ok = True)
    # If id is given we need to check if the instance was saved before. (The storage module is the one who defines ids)
    if id is not None:
        if(not os.path.isfile(_tofilepath(class_name, id))):
            raise ValueError(error.const.instance_with_id_doesnt_exist.format("", class_name, id))


def save(class_name, instance, id = None):
    """ save can be used to save an instance under its class name.
    Params:
    class_name: string of class name of instance with its full path. If Class Bar is in module bar in package foo class_name would be: "foo.bar.Bar"
    instance: python instance which is to be saved.
    id: Id of the instance to be saved. If the id is none, save creates a new id and returns it. Else save overwrites the file's old state.
    
    """
    # Check for boundry errors.
    _do_error_checks(class_name, id)
    if(instance is None):
        raise ValueError(error.const.is_null.format("instance"))
    #if(not isinstance(instance, class_name)):
    #    raise ValueError(error.const.not_subtype.format(f"{instance}", class_name))

    # The path to the instance.
    # Instances are stored in a subfolder named after the type's name.
    path = _topath(class_name)
    
    # Generate id if id is not given.
    while id is None:
        id = uuid.uuid4().hex[:10].upper()
        if(os.path.isfile(_tofilepath(class_name, id))):
            id = None

    # Finish the path.
    path = _tofilepath(class_name, id)
    # file pointer
    # w+ overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.
    starttime = time.time()
    file_ = open(path, "wb+") 

    # Serialize the object:
    # jsonstring = jsonpickle.encode(instance)
    pickle.dump(instance, file_)

    # file.write(jsonstring)
    file_.close()
    endtime = time.time()
    logging.debug("Stored object of class {} in {:9.3f} seconds.".format(class_name, (endtime - starttime)))
    
    return id

def restore(class_name, id):
    # Retrieve the json serialized state
    instance = restore_state(class_name, id)
    
    # Decode and return the instance.
    # instance = jsonpickle.decode(jsonstring)
    return instance

def restore_state(class_name, id):
    # Boundary checks.
    _do_error_checks(class_name, id)
    # restore needs id to be assigend.
    if(id == None): 
        raise ValueError(error.const.is_null.format("id"))

    path = _tofilepath(class_name,id)
    # file pointer
    # r opens a file for reading only. 
    starttime = time.time()
    file_ = open(path, "rb") 
    jsonstring = pickle.load(file_)
    file_.close()
    endtime = time.time()
    logging.debug("Restored object of class {} in {:9.3f} seconds.".format(class_name, (endtime - starttime)))
    return jsonstring

def readfile(path):
    return open(path, "rb")

def writefile(path):
    return open(path, "wb")


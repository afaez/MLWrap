# TODO we need to implement the right marshalling system.
import json
import jsonpickle
import numpy
from pase.pase_dataobject import PASEDataObject
from pase.marshal.typeserializer import serialize, unserialize

def marshaltype(instance):
    if isinstance(instance, numpy.ndarray):
        instance = instance.tolist()
    return instance
   

def marshal(output):
    """ Returns the json serialized output of function calls which is sent back to clients:
    """
    # TODO: How should we return the return value?
    output = marshaltype(output)
    try:
        # If it is json serializable, do it:
        return_json = json.dumps(output)
    except TypeError as ex:
        # Else just parse it to string and return its string represtation. 
        return_json = jsonpickle.dumps(output, unpicklable=False)
        #print(ex)

    return return_json

def marshaldict(dict_):
    if isinstance(dict_, dict):
        for key in dict_:
            if isinstance(dict_[key], dict):
                marshaldict(dict_[key])
            else:
                dict_[key] = marshaltype(dict_[key])
        
    return marshal(dict_) 

def unmarshal(value):
    """ Parses from dictionary to Python Object:
    """
    if isinstance(value, dict) and "type" in value:
        return marshaltype(value["data"])
    elif isinstance(value, PASEDataObject):
        return value.data
    else:
        return value
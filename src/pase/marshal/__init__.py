
import json
import numpy
import jsonpickle

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
    except TypeError:
        # Else just parse it to string and return its string represtation. 
        return_json = jsonpickle.dumps(output, unpicklable=False)
    return return_json

def marshaldict(dict_):
    for key in dict_:
        dict_[key] = marshaltype(dict_[key])
    return marshal(dict_) 



def isknowntype(type_):
    """ Returns True if the type_ string given is known by the marshalling system.
    """
    return True # TODO implement marshalling system

def fromdict(dict_):
    """ Parses from dictionary to Python Object:
    """
    if "type" in dict_:
        return dict_["data"]
    else:
        return dict_
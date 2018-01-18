
import json
import numpy
import jsonpickle

def marshal(output):
    """ Returns the json serialized output of function calls which is sent back to clients:
    """
    # TODO: How should we return the return value?
    if isinstance(output, numpy.ndarray):
        output = output.tolist()
        
    try:
        # If it is json serializable, do it:
        return_json = json.dumps(output)
    except TypeError:
        # Else just parse it to string and return its string represtation. 
        return_json = jsonpickle.dumps(output, unpicklable=False)
    return return_json
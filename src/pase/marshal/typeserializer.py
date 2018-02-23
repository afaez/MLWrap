import importlib
import numpy
from numbers import Number
from collections import OrderedDict
from pase.servicehandle import ServiceHandle
from pase.pase_dataobject import PASEDataObject


def serializedict(dict_):
    if isinstance(dict_, dict):
        for key in dict_:
            if isinstance(dict_[key], dict):
                serializedict(dict_[key])
            else:
                dict_[key] = serialize(dict_[key])
        
        
    return dict_

def serialize(value):
    """ Serializes the given value to it's semantic type.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        return serializedict(value)
    if isinstance(value, list):
        serializedlist = [str(v) for v in value]
        return {"type" : "StringList", "data" : serializedlist}
    if isinstance(value, ServiceHandle):
        return {"type" : "ServiceHandle", "data" : value.to_dict()}
    if isinstance(value, PASEDataObject):
        type = value.type
        if type in semantic_types:
            serializer_module = importlib.import_module('pase.marshal.' + type + '_serializer')
            data = serializer_module.serialize(value.data)
            return {"type" : type, "data" : data}
       
        elif isinstance(value.data, bool):
            return {"type":"Boolean", "data" : value.data}
        elif isinstance(value.data, Number):
            return {"type":"Number", "data" : value.data}
        elif isinstance(value.data, str):
            return {"type":"String", "data" : value.data}
        else:
            raise ValueError(f"Type={type} is not semantic")
        
    if isinstance(value, bool):
        return {"type":"Boolean", "data" : value}
    if isinstance(value, Number):
        return {"type":"Number", "data" : value}
    if isinstance(value, str):
        return {"type":"String", "data" : value}
        
    # if isinstance(value, numpy.ndarray):
    #     return value.tolist()

    raise ValueError(f"Cannot serialize {value}")

semantic_types = ["ServiceHandle", "Instances", "Instance", "LabeledInstances", "LabeledInstance", "StringList"]

def unserialize(semnaticvalue):

    dataobject = PASEDataObject.fromdict(semnaticvalue)

    if dataobject.type in semantic_types:
        serializer_module = importlib.import_module('pase.marshal.' + dataobject.type + '_serializer')
        dataobject.data = serializer_module.unserialize(dataobject.data)
    
    return dataobject
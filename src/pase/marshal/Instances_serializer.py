
from pase.marshal import Instance_serializer
import numpy

def unserialize(data):
    unserialized = []
    for instance in data:
        unserialized.append(Instance_serializer.unserialize(instance))
    return unserialized



def serialize(data):
    if isinstance(data, numpy.ndarray):
        return data.tolist()
    if isinstance(data, list):
        return [Instance_serializer.serialize(x) for x in data]
    else:
        raise ValueError("Type mismatch: " + data)


import numpy
import math
def serialize(data):
    if isinstance(data, numpy.ndarray):
        return data.tolist()
    if isinstance(data, list):
        serialization = [] 
        for x in data:
            number_value = float(x)
            if math.isnan(number_value):
                serialization.append("NaN")
            else:
                serialization.append(number_value)
        return serialization
    else:
        raise ValueError("Type mismatch: " + data)

def unserialize(data):
    if isinstance(data, dict):
        return unserialize_sparse(data)
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Can't unserialize: {}".format(data))

def unserialize_sparse(data):
    instance = []
    for field in data:
        index = int(field)
        while len(instance) <= index:
            instance.append(0)
        instance[index] = data[field]
    return instance

def unserialize_dense(data):
    return data
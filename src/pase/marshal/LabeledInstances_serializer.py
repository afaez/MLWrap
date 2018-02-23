from pase.marshal import Instances_serializer
from pase.marshal import StringList_serializer
def unserialize(data):
    unserialized = {"labels" : data["labels"]}
    unserialized["instances"] = Instances_serializer.unserialize(data["instances"])
    return unserialized


def serialize(data):
    if isinstance(data, dict):
        if "instances" not in data or "labels" not in data:
            raise ValueError("Semantic mismatch: " + str(data))
        data["instances"] = Instances_serializer.serialize(data["instances"])
        data["labels"] = StringList_serializer.serialize(data["labels"])
        return data
    else:
        raise ValueError("Given data isn't a dictionary object: " + str(data))
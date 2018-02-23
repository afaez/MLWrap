from pase.marshal import Instance_serializer

def unserialize(data):
    data["attributes"] = Instance_serializer.unserialize(data["attributes"])
    return data



def serialize(data):
    if isinstance(data, dict):
        data["attributes"] = Instance_serializer.serialize(data["attributes"])
        data["label"] = str(data["label"])
        return data
    else:
        raise ValueError("Given data isn't a dictionary object: " + str(data))
from pase.servicehandle import ServiceHandle

def unserialize(data):
    handle = ServiceHandle.from_dict(data)
    return handle


def serialize(data):
    if isinstance(data, ServiceHandle):
        return data.to_dict()
    else:
        raise ValueError("Given data isn't a servicehandle object: " + str(data))

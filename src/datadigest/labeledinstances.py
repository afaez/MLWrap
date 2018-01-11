import json

class labeledinstances:
    """ Implements a plain python object based on jaicore data representation.
    instances: list of lists of float. 
    labels: list of strings.
    """
    def __init__(self, instances, labels):
        self.labels = labels
        self.instances = instances
    
    @classmethod
    def fromjson(cls, json_string):
        """ Parses the given input json string and returns a labeledinstance object.
        """
        # Parse the json data into input.
        input = json.loads(json_string)
        # Catch value errors.
        if "instances" not in input or "labels" not in input:
            raise ValueError("The Json string doesn't contain instances or labels field.")

        # Create object and return it.
        return cls(input["instances"],input["labels"])
    
    def tojson(self): 
        """ Creates a json string representing this instance.
        """
        # Encode this object into json string.
        output = json.dumps({"instances" : self.attributes, "labels" : self.label})
        # Catch value errors.
        if self.instances is None or self.labels is None:
            raise ValueError("Label or attributes are None")

        return output


        
        
import json

class labeledinstance:
    """ Implements a plain python object based on jaicore data representation.
    attributes: list of float. the built-in list type to store the data.
    label: string.
    """
    def __init__(self, attributes, label):
        self.label = label
        self.attributes = attributes
    
    @classmethod
    def fromjson(cls, json_string):
        """ Parses the given input json string and returns a labeledinstance object.
        """
        # Parse the json data into input.
        input = json.loads(json_string)
        # Catch value errors.
        if "attributes" not in input or "label" not in input:
            raise ValueError("The Json string doesn't contain attribute or label field.")

        if not isinstance(input["label"] , str): 
            raise ValueError("Label content isn't a string value.")

        if not isinstance(input["attributes"] , list): 
            raise ValueError("Attributes content isn't a list.")
        
        # Create object and return it.
        return cls(input["attributes"],input["label"])
    
    def tojson(self): 
        """ Creates a json string representing this instance.
        """
        # Encode this object into json string.
        output = json.dumps({"attributes" : self.attributes, "label" : self.label})
        # Catch value errors.
        if self.attributes is None or self.label is None:
            raise ValueError("Label or attributes are None")

        if not isinstance(self.label, str): 
            raise ValueError("Label content isn't a string value.")

        if not isinstance(self.attributes, list): 
            raise ValueError("Attributes content isn't a list.")

        return output


        
        
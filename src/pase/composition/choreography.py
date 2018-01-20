from .operation import Operation, splitintwo
from collections import defaultdict # for parameters
import json
import pase.marshal 
import logging

class Choreography:
    """Datastructure that holds information about operations and return value.

    Fields:
        operation_list = list of Operation Objects
        return_list = string list of return values
        store_list = string list of store values.
    """
    def __init__(self, operation_list, return_list, store_list):
        self.operation_list = operation_list
        self.return_list = return_list
        self.store_list = store_list
        self.currentindex = 0

    def __iter__(self):
        return iter(self.operation_list)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"ops:{self.operation_list}\nreturns:{self.return_list}\nstores:{self.store_list}"

    @classmethod 
    def fromstring(cls, choreography):
        """ Creates a Choreography object from a string. 
        This method conforms to the implementation of JASE.
        """
        if not choreography: 
            # the given string is null or empty
            raise ValueError("None or empty string was given.")

        choreography = choreography.strip()
        pairs = choreography.split("&") # split by '&'
        # create parameter object
        parameters = {}
        for pair in pairs:
            parameter = pair.split("=", 1) 
            # split only returns on array of size two: "A=B=C" -> ["A", "B=C"]
            if len(parameter) < 2:
                continue
            key = parameter[0]
            value = parameter[1]
            if key in parameters:
                # key was already found. add to the list in the dictionary:
                list_ = list(parameter[key])
                list_.append(value)
                parameters[key] = list_
            else:
                # First time adding
                parameters[key] = value

        # Extract coreography and index
        if "coreography" not in parameters:
            raise ValueError("This service can only execute choreographies")
        choreography_string = parameters["coreography"]
        if "currentindex" not in parameters:
            currentindex = 0
        else:
            currentindex = parameters["currentindex"]

        # json deserialise inputs and put them by their indexes into 'inputs' dictionary
        inputs = {}
        for key in parameters:
            if not key.startswith("inputs"):
                # this is not an input
                continue

			# Extract index from brackets. e.g.: inputName =  "inputs[i1]" -> index = "i1"
            index = find_between(key, '[', ']')
            input_stringvalue = str(parameters[key])
            input_object = json.loads(input_stringvalue)

            if "type" not in input_object:
                # the json input doesn't have a type field.
                raise ValueError(f"No type field in inputs[{index}]={input_stringvalue}")
            if not pase.marshal.isknowntype(input_object["type"]):
                # The given type isn't known by the marshalling system.
                type_ = input_object["type"]
                raise ValueError(f"The given type = {type_} isn't known by the marshalling system.")
            inputs[index] = input_object

        # Now reuse fromdict method from below:
        logging.debug("Parsing choero : "+ choreography_string)
        request_dictionary = {"execute" : choreography_string, "input" : inputs}
        choreo = Choreography.fromdict(request_dictionary)
        choreo.currentindex = currentindex
        return choreo

    @classmethod
    def fromjson(cls, jsonstring):
        """ Creates a Choreography object from a json string.
        """
        import json
        return Choreography.fromdict(json.loads(jsonstring))

    @classmethod
    def fromdict(cls, dictionary, return_all=False):
        """ Creates an Choreography object from a dictionary.
        if return_all is set to True the choreography is set to return all created objects.
        """
        if "execute" not in  dictionary:
            raise ValueError("Dictionary doesn't contain execute entry.")
        if "return" not in dictionary:
            # no return specified. return all
            return_all = True 

        operation_stringlist = dictionary["execute"].split(";")
        operation_list = []

        # Extract "input", "return" and "store" from the json call.
        input_dict = {} # Holds input values.
        if "input" in dictionary:
            try:
                input_dict = dict(dictionary["input"])
            except Exception:
                pass
        # Parse the input data
        for inputkey in input_dict:
            input_dict[inputkey] = pase.marshal.fromdict(input_dict[inputkey])

        store_list = dictionary["store"] if "store" in dictionary else []
        
        for operation_string in operation_stringlist:
            if "::" not in operation_string:
                continue
            operation_string = operation_string.strip() # In java: "s ".trim() => "s"
            leftside, rightside = splitintwo(operation_string, "=")


            if leftside is None or leftside == 0:
                # Syntax error. Ignore. TODO should we keep ignoring this?
                continue

            elif len(rightside) == 0:
                # Just a call, like: operation_string = "foo.bar()"
                assignname = None # rightside is empty
                calloperation = leftside # leftside contains call operation
            else  :
                # Assignment, like: operation_string = "a = foo.bar()"
                assignname = leftside
                calloperation = rightside

                if("::" in assignname) :
                    assignname = None
                    calloperation = operation_string.strip()
            try:
                op = Operation(assignname, calloperation, input_dict) # Try to parse the operation 
                operation_list.append(op)

            except ValueError:
                pass 
        
        if(return_all):
            # add all to be created instances to the return list
            return_list = []
            for operation in operation_list:
                if operation.leftside is not "empty":
                    return_list.append(operation.leftside)
        else:
            # retrieve return list from the input dictionary
            return_list = dictionary["return"]

        
        return Choreography(operation_list, return_list, store_list) 
        # Returns structure containing all operations and inputs and so on.

def find_between(s, first, last):
    """ Extracts the substring in between two delimiters.
    """
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
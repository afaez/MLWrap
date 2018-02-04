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
    def __init__(self, originalstring, operation_list, return_list, store_list, input_dict):
        self.originalstring = originalstring
        self.operation_list = operation_list
        self.return_list = return_list
        self.store_list = store_list
        self.input_dict = input_dict
        self.currentindex = 0
        self.maxindex = len(operation_list)


    def __iter__(self):
        return iter(self.operation_list)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"ops:{self.operation_list}\nreturns:{self.return_list}\nstores:{self.store_list}"


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
        # for inputkey in input_dict:
        #     input_dict[inputkey] = pase.marshal.unmarshal(input_dict[inputkey])

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
                op = Operation(assignname, calloperation) # Try to parse the operation 
                operation_list.append(op)

            except ValueError:
                pass 
        
        if(return_all):
            # add all to be created instances to the return list
            return_list = []
            for operation in operation_list:
                if operation.leftside == "empty":
                    continue
                if operation.host == "$empty$":
                    return_list.append(operation.leftside)
                
            # return_list.append(operation_list[-1].leftside)
        else:
            # retrieve return list from the input dictionary
            return_list = dictionary["return"]

        
        choreo = Choreography(dictionary["execute"], operation_list, return_list, store_list, input_dict) 

        if "currentindex" in dictionary:
            choreo.currentindex = int(dictionary["currentindex"])
        if "maxindex" in dictionary:
            choreo.maxindex = int(dictionary["maxindex"])

        return choreo
        # Returns structure containing all operations and inputs and so on.

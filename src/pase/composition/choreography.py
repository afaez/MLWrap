from .operation import Operation, splitintwo



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
    def fromdict(cls, dictionary):
        """ Creates an Choreography object from a dictionary.
        """
        if ("execute" not in  dictionary) or ("return" not in dictionary):
            raise ValueError("Dictionary doesn't contain execute or out entry.")
        operation_stringlist = dictionary["execute"].split(";")
        operation_list = []

        # Extract "input", "return" and "store" from the json call.
        input_dict = {} # Holds input values.
        if "input" in dictionary:
            try:
                input_dict = dict(dictionary["input"])
            except Exception:
                pass

        return_list = dictionary["return"]
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
        
        return Choreography(operation_list, return_list, store_list) # Returns structure containing all operations and inputs and so on.



from .operation import Operation, splitintwo
from collections import defaultdict # for parameters
import json
import pase.marshal 
from pase.servicehandle import ServiceHandle
import logging
import re
from pase import store

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
    def todict(cls, composition=None, maxindex = -1, currentindex=-1, variables = {}):
        """ Creates a dictionary object from this choreography
        """
        d = dict()
        if composition is not None and isinstance(composition, str):
            d["choreography"] = composition
        if maxindex >= 0:
            d["maxindex"] = maxindex
        if currentindex >= 0:
            d["currentindex"] = currentindex

        if isinstance(variables, dict):
            regex = "^i(\d+)$"
            arglist = []
            translatedVars = {"$arglist$" : arglist}
            for fieldname in variables.keys():
                if(variables[fieldname] is None):
                    translatedVars[fieldname] = None

                fieldvalue = pase.marshal.serialize(variables[fieldname])
                match = re.match(regex, fieldname)
                if match is not None:
                    index = int(match.group(1)) - 1 
                    while len(arglist) <= index:
                        arglist.append(None)
                    arglist[index] = fieldvalue
                else:
                    translatedVars[fieldname] = fieldvalue


        d["inputs"] = translatedVars

        return d
        
    @classmethod
    def fromjson(cls, jsonstring):
        """ Creates a Choreography object from a json string.
        """
        import json
        return Choreography.fromdict(json.loads(jsonstring))

    @classmethod
    def fromdict(cls, dictionary, return_all=False, translate_positional_args=True, remote_host=None):
        """ Creates an Choreography object from a dictionary.
        if return_all is set to True, the choreography is set to return all created objects.
        if translate_positional_args is True, positional arguments in $arglist$ are translates to i1, i2, ..
        """
        # if "choreography" not in  dictionary:
        #     raise ValueError("Dictionary doesn't contain execute entry.")
        if "return" not in dictionary:
            # no return specified. return all
            return_all = True 
        

        # Extract "input", "return" and "store" from the json call.
        input_dict = {} # Holds input values.
        if "inputs" in dictionary:
            try:
                input_dict = dict(dictionary["inputs"])
            except Exception:
                pass
        # traslate arglist fields to fieldnames
        if translate_positional_args:
            arglist = input_dict.pop("$arglist$", [])
            for i in range(len(arglist)):
                input_dict["i"+(str(i+1))] = arglist[i]

            for fieldname in input_dict.keys():
                # print("unserializing {}: ".format(fieldname) + str(input_dict[fieldname])[0:200])
                pdo = pase.marshal.unserialize(input_dict[fieldname])
                if(pdo.type == "ServiceHandle"):
                    handle = pdo.data
                    if remote_host is not None:
                        #reassign hostnames:
                        if not handle.is_remote():
                            handle.host = remote_host

                    if not pdo.data.is_remote():
                        # load service from disk
                        serviceinstance = store.restore(handle.classpath, handle.id)
                        handle.service = serviceinstance

                    input_dict[fieldname] = handle
                else:
                    input_dict[fieldname] = pdo

        # Parse the input data
        # for inputkey in input_dict:
        #     input_dict[inputkey] = pase.marshal.unmarshal(input_dict[inputkey])

        store_list = dictionary["store"] if "store" in dictionary else []
        
        if "choreography" in dictionary:
            compositionstring = dictionary["choreography"]
            operation_stringlist = compositionstring.split(";")
            operation_list = []

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
        else:
            operation_list = []
            compositionstring = ""
        
        if(return_all):
            # add all to be created instances to the return list
            return_list = []
            for operation in operation_list:
                if operation.leftside == "empty":
                    continue
                if operation.leftside in input_dict:
                    continue
                return_list.append(operation.leftside)
                
            # return_list.append(operation_list[-1].leftside)
        else:
            # retrieve return list from the input dictionary
            return_list = dictionary["return"]

        logging.debug(f"return list: {return_list}")
        choreo = Choreography(compositionstring, operation_list, return_list, store_list, input_dict) 

        if "currentindex" in dictionary:
            choreo.currentindex = int(dictionary["currentindex"])
        if "maxindex" in dictionary:
            choreo.maxindex = int(dictionary["maxindex"])

        return choreo
        # Returns structure containing all operations and inputs and so on.

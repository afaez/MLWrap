""" Module contains Operation class which parses operation information from string. 
"""
import json
import re # regular expression
from pase.servicehandle import ServiceHandle

class Operation:
    """ This class parses an operation of the form: 
        <object-name> = <class/object-name>::<functionname>({<$arglist$>})
    into fields that make it easier to execute it.
    """
    # The string before the first '/' . contains the host name this operation is to be executed on.
    host = "$empty$"
    # The left side string of the equal sign. contains the object name which will be assigned to the return value of this operation.
    leftside = "empty"
    # The right side string of the equal sign. contains 'clazz', 'func' and 'args' as string.
    rightside = ""
    # The substring that comes before '::' in rightside. contains the class path or object name.
    clazz = ""
    # The substring that comes after '::' but before '(' in rightside. contains the function name.
    func = ""
    # The argument dictionary. contains keywords mapping to value, like: {"a":5} but it also maps "$arglist$" to a positional list of arguments for the function call, like: [5,"stringvalue"]
    args = {"$arglist$":[]}


    def __init__(self, leftside, rightside):
        """ Extracts the operation information from the leftside and rightside string.
        """
        self.leftside = leftside if leftside is not None else leftside
        if "/" in rightside:
            self.host, rightside =  splitintwo(rightside, "/")
        self.rightside = rightside
        self.clazz, call = splitintwo(rightside, "::")
        if self.clazz is None: 
            raise ValueError() # syntax error in class: no double colon
        self.func, given_args = splitintwo(call, "(")
        if(self.func is None):
            raise ValueError() # syntax error in func name: no parenthesis 


        # extract parameters. (function arguments)
        self.args = {"$arglist$":[]}
        if len(given_args) == 0: 
            # I know i can use 'if len(given_args):' or 'if given_args:' instead. 
            # But this condition check is more readable in my opinion. 
            return
        parameters, _ = splitintwo(given_args, ")")
        if (len(parameters) >= 2  and (parameters[0] == '{' and parameters[-1] == '}')):
            # Parameters are given. 
            parameters = parameters[1:-1]
            parameterlist = parameters.split(",")
            for param in parameterlist:
                fieldname, argvaluestring = splitintwo(param, "=")
                if fieldname is not None:
                    # if json can parse the argument value then it must be some primary data like numbers or array of numbers.
                    try:
                        argvalue = json.loads(argvaluestring) # try to parse the value.
                    except Exception:
                        argvalue = argvaluestring
                    if re.match("^i[0-9]+$", fieldname): 
                        # if the fieldname matches the pattern it is a positional argument. like i1, i2...
                        # extract fieldname: fieldname = i10 -> index = 10
                        index = int(fieldname[1:]) - 1
                        # insert value in the $arglist$ array in position=index:
                        while len(self.args["$arglist$"]) <= index:
                            self.args["$arglist$"].append(None)
                        self.args["$arglist$"][index] = argvalue
                    else:
                        # assign the keyword argument its value.
                        self.args[fieldname] = argvalue

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"{self.leftside} = {self.clazz}.{self.func}"

    def canexecute(self, state = {}):
        """ Returns True if the operation can be execution given the state of the system.
        """
        import pase.config
        if self.clazz not in state:
            # this is a constructor:
            return pase.config.lookup.class_known(self.clazz + "." + self.func)
        else:
            field = state[self.clazz]
            if isinstance(field, ServiceHandle):
                return not field.is_remote()
            else:
                return False
            # # return true if all arguments the operation needs
            # return all(argument_ in stat for argument_ in self.args)



def splitintwo(text, char):
    """ Splits the 'text' into two string objects which are divided by the 'char' character.
    e.g.: splitintwo("foobar", b) returns: "foo" , "ar"
    """
    position = text.find(char)
    if(position == -1):
        # return None if split character isn't contained in the given string. 
        # this is just the definition of splitintwo.
        return None, None
    # Divide string into two substrings
    return text[:position].strip(), text[position+len(char):].strip()
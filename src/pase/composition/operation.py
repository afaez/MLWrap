import json
class Operation:
    def __init__(self, leftside, rightside, input_dict):

        self.leftside = leftside if leftside is not None else "$empty$"
        if "/" in rightside:
            self.host, rightside =  splitintwo(rightside, "/")
        else: 
            self.host = "empty"
        self.rightside = rightside
        self.clazz, call = splitintwo(rightside, "::")
        if self.clazz is None: 
            raise ValueError() # syntax error in class: no double colon
        self.func, args = splitintwo(call, "(")
        if(self.func is None):
            raise ValueError() # syntax error in func name: no parenthesis 

        self.args = {}
        if len(args) == 0: 
        # I know i can use 'if len(args):' or 'if args:' instead. 
        # But this condition is more readable in my opinion. 
            return

        parameters, _ = splitintwo(args, ")")

        if (len(parameters) >= 2  and (parameters[0] == '{' and parameters[-1] == '}')):
            parameters = parameters[1:-1]
            parameterlist = parameters.split(",")
        else:
            return
            
        for param in parameterlist:
            fieldname, argvaluestring = splitintwo(param, "=")
            if fieldname is not None:
                if isinstance(argvaluestring,str) and  argvaluestring in input_dict:
                    argvalue = input_dict[argvaluestring] # try to retrieve the data from input dictionary
                else:
                    try:
                        argvalue = json.loads(argvaluestring) # try to parse the value
                    except Exception:
                        argvalue = argvaluestring

                self.args[fieldname] = argvalue

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"{self.leftside} = {self.clazz}.{self.func}"

    
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
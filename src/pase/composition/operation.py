import json
class Operation:
    def __init__(self, leftside, rightside, input_dict):
        self.leftside = leftside if leftside is not None else "empty"
        self.rightside = rightside
        splitting = rightside.split("::")
        if(len(splitting) != 2):
            raise ValueError()
        self.clazz = splitting[0].strip()
        call = splitting[1]
        splitting = call.split("(")
        if(len(splitting) != 2):
            raise ValueError()
        self.func = splitting[0]
        args = splitting[1]
        splitting = (" " + args).split(")")
        if(len(splitting) == 0):
            raise ValueError()
        argsstring = splitting[0].strip()
        if (len(argsstring) >= 2  and (argsstring[0] == '{' or argsstring[-1] == '}')):
            argsstring = argsstring[1:-1]
        splitting = argsstring.split(",")
        self.args = {}
        for argstring in splitting:
            args = argstring.split("=")
            if(len(args) == 2):
                fieldname = args[0].strip()
                argvaluestring = args[1].strip()
                if argvaluestring in input_dict:
                    argvalue = input_dict[argvaluestring]
                else:
                    try:
                        argvalue = json.loads(argvaluestring)
                    except Exception:
                        raise ValueError()
                self.args[fieldname] = argvalue

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"{self.leftside} = {self.clazz}.{self.func}"

    
class PASEDataObject():
    """
    """
    type = None
    data = None
    def __init__(self, type, data):
        self.type = type
        self.data = data

    @classmethod
    def fromdict(cls, dic):
        return PASEDataObject(dic["type"], dic["data"])

    def todict(self):
        return {"type" : self.type, "data" : self.data}

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "<<type: " + str(self.type) + " data: " + str(self.data)+ ">>"

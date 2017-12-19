
class B:
    """ Dummy class B.
    Contains 2 numbers: a and b.
    """
    def __init__(self, a , b):
        self.a = a
        self.b = b
    
    def calc(self, c):
        return self.a + self.b * c
    
    def __str__(self):
        return f"a = {self.a} b = {self.b}"

class A:
    """ Dummy class A.
    References any object.
    """
    def __init__(self, ref):
        self.ref = ref

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
        return "a = {} b = {}".format(self.a, self.b)

    @classmethod
    def random(cls):
        from random import randint
        b = B(randint(0, 9), randint(0, 9))
        return b

class A:
    """ Dummy class A.
    References any object.
    """
    def __init__(self, ref):
        self.ref = ref
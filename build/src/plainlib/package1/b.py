
class B:
    def __init__(self, a , b):
        self.a = a
        self.b = b
    
    def calc(self, c):
        return self.a + self.b * c
    
    def __str__(self):
        return f"a = {self.a} b = {self.b}"

class A:
    def __init__(self, B):
        self.B = B
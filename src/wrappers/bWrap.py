""" This module contains a wrapper for plainlib.package1.b.B.
"""
from plainlib.package1.b import B
from .wrappercore import DelegateFunctionsMixin

class BWrap(DelegateFunctionsMixin):

    def __init__(self, wrappedclass_module, kwargs):
        self.instance  = wrappedclass_module(a=kwargs["b"], b=kwargs["a"]) # switch the arguments
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        DelegateFunctionsMixin.__init__(self, delegate=self.instance)

    def calc2(self, a):
        return a + self.instance.a

""" Defines usefull mixins that can be extended by wrapper classes.
"""

class DelegateFunctionsMixin(object):
    """ Delegate accesses to a delegate.
    """
    delegate = None
    def __init__(self, delegate):
        self.delegate = delegate

    def __getattr__(self, name):
        """ Attributes are accessed that aren't defined by the subclass. 
        Redirect to delegate if it is defined.
        """
        if self.delegate is not None and hasattr(self.delegate, name):
            return getattr(self.delegate, name)
        else:
            getattr(super(),name)
    
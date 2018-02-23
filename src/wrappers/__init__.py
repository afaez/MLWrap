"""This module contains wrappers used to encapsulate classes to offer services. 
Classes in this package should overwrite the needed methods with the desired signature.

The remaining function which are not overwritten, are automatically delegated to the instance.

The __init__ signature of wrapper must be:
    def __init__(self, wrappedclass_module,  kwargs):
wrappedclass_module is the module of the wrapped class. you can call its constructor with: wrapped_class_module()
kwargs is a dictionary of given arguments with labels. It is guaranteed that every required argument has an entry in kwargs.
"""
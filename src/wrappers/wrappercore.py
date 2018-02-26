""" Defines usefull mixins that can be extended by wrapper classes.
"""
import json
import logging
ATTRIBUTE_BLACKLIST = ["__getstate__", "__setstate__"]
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
        if name not in ATTRIBUTE_BLACKLIST and self.delegate is not None and hasattr(self.delegate, name):
            return getattr(self.delegate, name)
        else:
            getattr(super(),name)


class BaseOptionsSetterMixin(object):
    """ Mixin for setting options. 
    The wrapper inheriting this mixin can either wrap a object that has 'get_params' and 'set_params' methods or specify it by itself.
    """

    def optionsFromDict(self, kwargs):
        """ This method invoked the setOptions method by using the first list in keyword arguments.
        """
        logging.debug("Setting options: " + str(kwargs))
        if "$arglist$" in kwargs:
            for arg in kwargs["$arglist$"]:
                 if isinstance(arg, list):
                    # its a string list. invoke set options
                    self.setOptions(arg)
        

        for key in kwargs:
            if key == "$arglist$":
                continue
            if isinstance(kwargs[key], list):
                # its a string list. invoke set options
                self.setOptions(kwargs[key])
            else:
                self.setOption(key, kwargs[key])
    
    def setOptions(self, stringlist):
        """ iterates over the string list and parses each given option and invokes setOption.
        """
        for option in stringlist:
            option = str(option)
            try:
                # options contains field and value, like: -a 1
                splits = option.split(" ", 2)
                field = splits[0][1:] # use[1:] to cut off the '-'
                value = json.loads(splits[1])

                self.setOption(field,value)
                
            except Exception as e:
                logging.error("Error {} during setOptions of: {}".format(e, option))
                pass
    
    def setOption(self, field, value):
        """ Uses the get_params and set_params method to assign the given value to the given field.
        """
        if hasattr(self, "get_params") and hasattr(self, "set_params"):
            if field in self.get_params().keys():
                logging.debug("Setting field={} to value={}".format(field,value))
                self.set_params(**{field:value})
        # else:
        #     self.__dict__[field] =  value
        




    

import pase.marshal

class BaseClassifierMixin(object):

    def declare_classes(self, X):
        """ Declare the class labels to predict to.
        The first time this method only uniquely stores labels from X into a list.
        If declare_classes has been called before (self.classlables is assigned) this method only checks if the labels in X are all contained in the stored list. Else it will raise a value error.

        X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        raise Exception("Not Implemented")

    def train(self, X):
        """ Trains this neural network.

        X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        raise Exception("Not Implemented")

    def predict(self, X):
        """ Does prediciton using the wrapped neural network based on input X.

        X is instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        X may also be a dictionary object of labeledinstances. (Used when testing with labeledinstances)
        """
        raise Exception("Not Implemented")
    
    def predict_and_score(self, X, normalize=True):
        """ First predicts the input objects using the predict method. Then calculated the accuracy of the model and return it.
        X: LabeledInstance
        normalize: If ``False``, return the number of correctly classified samples.
        Otherwise, return the fraction of correctly classified samples.
        """
        y_pred = pase.marshal.unmarshal(self.predict(X))
        y_true = X["labels"]
        score = 0 
        if isinstance(y_pred, list):
            #count matches
            for i in range(len(y_pred)):
                if y_pred[i] == y_true[i]:
                    score += 1

        if normalize:
            score = float(score) / len(y_pred) # normalize if needed.
            return round(score, 2)
        else:
            return int(score)

    
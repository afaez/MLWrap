""" Defines usefull mixins that can be extended by wrapper classes.
"""
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

    
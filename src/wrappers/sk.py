""" Wraps scikit learn libreries. """
from wrappers import wrappercore
import pase.marshal
import sklearn.preprocessing
from pase.pase_dataobject import PASEDataObject
import logging

def normalize_labeledinstances(wrappedclass_module, kwargs):
    """ Wrapper for method.
    """
    labeledinstances = kwargs.pop('X', None)
    instances = labeledinstances["instances"]
    labeledinstances["instances"] = sklearn.preprocessing.normalize(instances, **kwargs)
    
    dataobject = PASEDataObject("LabeledInstances", labeledinstances)
    return dataobject

class WrappedClassifier(wrappercore.DelegateFunctionsMixin, wrappercore.BaseClassifierMixin, wrappercore.BaseOptionsSetterMixin):
    """ Wraps two functions: train and predict.
    declare_classes has the signature: declare_classes(LabeledInstances)::void
    fit (also callable by 'train') has the new signature:  fit(LabeledInstances)::void
    predict has the new signature: predict(Instances)::LabeledInstances
    Classifiers can deal with classes as strings themselves.
    """
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module() 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)
        wrappercore.BaseOptionsSetterMixin.optionsFromDict(self, kwargs)
        

    def declare_classes(self, X):
        """ Does nothing for now.
        """
        pass

    def train(self, X):
        """ Redirects to fit.
        """
        #logging.debug("----> Start training with:"  + str(X))
        self.fit(X)

    def fit(self, X):
        """ X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        # print(X["instances"].tolist())
        # print(X["labels"])
        # call fit method
        if isinstance(X, dict):
            self.delegate.fit(X["instances"], X["labels"])
        else:
            raise Exception("Fit invocation on:\n" + str(X))

    def predict(self, X):
        """ X is instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        X may also be a dictionary object of labeledinstances. (Used when testing with labeledinstances)
        """
        #logging.debug("----> Start predicting with:"  +  str(X))
        if(isinstance(X, dict)):
            X = X["instances"]
        prediction = self.delegate.predict(X)
        # prediction is an array of classes: ["A", "B", ..]
        dataobject = PASEDataObject("StringList", prediction.tolist())
        return dataobject




class SkPPWrapper(wrappercore.DelegateFunctionsMixin, wrappercore.BaseOptionsSetterMixin):
    """ Wraps the feature selection classes in scikit.
    """
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module() 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)
        wrappercore.BaseOptionsSetterMixin.optionsFromDict(self, kwargs)
    
    def fit(self, X):
        """ X is labeledinstances object.
        """ 
        # call fit method with instances only
        self.delegate.fit(X["instances"], X["labels"]) 

    def transform(self, X):
        output = self.delegate.transform(X["instances"])
        X_copy = dict(X)
        X_copy["instances"] = output
        dataobject = PASEDataObject("LabeledInstances", X_copy)
        return dataobject

    def train(self, X):
        self.fit(X)

    def preprocess(self, X):
        return self.transform(X)

class ImputerWrapper(wrappercore.DelegateFunctionsMixin, wrappercore.BaseOptionsSetterMixin):
    """ Wraps the imputer from sk.
    """
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module() 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)
        wrappercore.BaseOptionsSetterMixin.optionsFromDict(self, kwargs)

    def fit(self, X):
        """ X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        # call fit method with instances only
        self.delegate.fit(X["instances"]) 

    def transform(self, X):
        """ X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        imputedinstances = self.delegate.transform(X["instances"])
        X_copy = dict(X)
        X_copy["instances"] = imputedinstances
        dataobject = PASEDataObject("LabeledInstances", X_copy)
        return dataobject



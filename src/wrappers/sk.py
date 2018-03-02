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
        if(isinstance(X, dict)):
            X = X["instances"]
        prediction = self.delegate.predict(X)
        # prediction is an array of classes: ["A", "B", ..]
        dataobject = PASEDataObject("StringList", prediction.tolist())
        return dataobject



# Delegates other classes
class WrappedNumClassifier(wrappercore.DelegateFunctionsMixin, wrappercore.BaseClassifierMixin):
    """ Wraps a predictor to Work like a classifier.
    fit has the new signature:  fit(LabeledInstances)::void
    predict has the new signature: fit(Instances)::LabeledInstances
    """
    # Maps labels to numerical values
    labelslist = []
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module() 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)

    def train(self, X):
        return self.fit(X)

    def fit(self, X):
        # X is now a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        # extend the labelsmapping
        y_data = []
        for label in X["labels"]:
            if label not in self.labelslist:
                self.labelslist.append(label)# first label found is mapped to 0, second to 1, etc..
            # create y_data of numerical values: [0,2,1,3,0 .. ]
            y_data.append(self.labelslist.index(label))
        # now call fit method
        self.delegate.fit(X["instances"].tolist(), y_data)

    def predict(self, X):
        # X is now instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        # First predict to numerical values
        if(isinstance(X, dict)):
            X = X["instances"]
        prediction = self.delegate.predict(X)
        labeledprediction = []
        # now map back to labels
        for index in range(len(prediction)):
            rounded_outcome = int(round(prediction[index])) # round(0.5) => 0 ; round(0.51) => 1
            if(rounded_outcome>=0 and rounded_outcome<len(self.labelslist)):
                # in bound of mapping
                labeled_outcome = self.labelslist[rounded_outcome]
            # else project to the boundaries
            elif rounded_outcome<0:
                labeled_outcome = self.labelslist[0] # first label
            else:
                labeled_outcome = self.labelslist[-1] # last label
            labeledprediction.append(labeled_outcome)
        
        dataobject = PASEDataObject("StringList", labeledprediction)
        return labeledprediction


class SkPPWrapper(wrappercore.DelegateFunctionsMixin, wrappercore.BaseOptionsSetterMixin):
    """ Wraps the feature selection classes in scikit.
    """
    trained = False
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
        self.trained = True

    def transform(self, X):
        output = self.delegate.transform(X["instances"])
        X_copy = dict(X)
        X_copy["instances"] = output
        dataobject = PASEDataObject("LabeledInstances", X_copy)
        return dataobject


    def preprocess(self, X):
        if not self.trained:
            self.fit(X)

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



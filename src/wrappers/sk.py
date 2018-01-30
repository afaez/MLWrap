from wrappers import wrappercore
import sklearn.preprocessing

def normalize_labeledinstances(wrappedclass_module, kwargs):
    """ Wrapper for method.
    """
    labeledinstances = kwargs.pop('X', None)
    instances = labeledinstances["instances"]
    labeledinstances["instances"] = sklearn.preprocessing.normalize(instances, **kwargs)
    return labeledinstances

# Delegates other classes
class WrappedClassifier(wrappercore.DelegateFunctionsMixin):
    """ Wraps two functions: fit and predict.
    fit has the new signature:  fit(LabeledInstances)::void
    predict has the new signature: fit(Instances)::LabeledInstances
    Classifiers can deal with classes as strings themselves.
    """
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module(**kwargs) 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)

    def fit(self, X):
        """ X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        # call fit method
        self.delegate.fit(X["instances"], X["labels"])

    def predict(self, X):
        # X is now instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        # X may also be a dictionary object of labeledinstances. (Used when testing with labeledinstances)
        if(isinstance(X, dict)):
            X = X["instances"]
        prediction = self.delegate.predict(X)
        # prediction is an array of classes: ["A", "B", ..]
        return prediction

    def predict_and_score(self, X, normalize=True):
        """ First predicts the input objects using the predict method. Then calculated the accuracy of the model and return it.
        X: LabeledInstance
        normalize: If ``False``, return the number of correctly classified samples.
        Otherwise, return the fraction of correctly classified samples.
        """
        y_pred = self.predict(X)
        y_true = X["labels"]
        matching = y_true == y_pred # array of 1 and 0, based on if it was a match or not.
        score = matching.sum() # count matches.
        if normalize:
            score = float(score) / len(y_pred) # normalize if needed.
            return score
        else:
            return int(score)

# Delegates other classes
class WrappedPredictorToClassifier(wrappercore.DelegateFunctionsMixin):
    """ Wraps a predictor to Work like a classifier.
    fit has the new signature:  fit(LabeledInstances)::void
    predict has the new signature: fit(Instances)::LabeledInstances
    """
    # Maps labels to numerical values
    labelslist = []
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module(**kwargs) 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)

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
        self.delegate.fit(X["instances"], y_data)

    def predict(self, X):
        # X is now instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        # First predict to numerical values
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
        
        return labeledprediction

class ImputerWrapper(wrappercore.DelegateFunctionsMixin):
    """ Wraps the imputer from sk.
    """
    def __init__(self, wrappedclass_module, kwargs):
        wrappedinstance  = wrappedclass_module(**kwargs) 
        # initialize the DelegateFunctionsMixin with the created wrapped object.
        wrappercore.DelegateFunctionsMixin.__init__(self, delegate=wrappedinstance)

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
        return X_copy



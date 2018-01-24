from wrappers import wrappercore
import sklearn.preprocessing

def normalize_labeledinstances(wrappedclass_module, kwargs):
    """ Wrapper for method.
    """
    labeledinstances = kwargs.pop('X', None)
    instances = labeledinstances["instances"]
    labeledinstances["instances"] = sklearn.preprocessing.normalize(instances, **kwargs)
    return labeledinstances


class WrappedPredictor(wrappercore.DelegateFunctionsMixin):
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


            


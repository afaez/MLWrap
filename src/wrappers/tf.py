""" Wraps tensorflow library in tflib """

from wrappers import wrappercore
import pase.marshal
from pase.pase_dataobject import PASEDataObject
import jsonpickle
import jsonpickle.handlers
from tflib.neuralnet import NeuralNet
from tflib.arffcontainer import ArffStructure


class NeuralNetHandler(jsonpickle.handlers.BaseHandler):    
    # handler for jsonpickle to save a neuralnet object
    def flatten(self, obj, data):
        data["layer_count"] = obj.layer_count
        data["trained"] = obj.trained
        if obj.trained:
            data["in_size"] = obj.in_size 
            data["out_size"] = obj.out_size 
            data["weight_biases"] = obj.model_values
            pass
        return data

    def restore(self, data):
        obj = WrappedNeuralNet(None, data["layer_count"])
        trained = data["trained"]
        if trained:
            obj.trained = True
            obj.in_size = data["in_size"]
            obj.out_size = data["out_size"]
            obj.model_values = data["weight_biases"]
        


    

# Register this handler for the class
jsonpickle.handlers.registry.register(NeuralNet, NeuralNetHandler)

class WrappedNeuralNet(wrappercore.BaseClassifierMixin, wrappercore.BaseOptionsSetterMixin):
    """ Wrapper for neuralnet module in tflib.
    Offers our standard methods: declare_classes, train and predict
    declare_classes has the signature: declare_classes(LabeledInstances)::void
    train has the signature:  train(LabeledInstances)::void
    predict has the signature: predict(Instances)::LabeledInstances
    Classifiers can deal with classes as strings themselves.
    """
    model_values = None
    layer_count = 2
    def __init__(self, wrappedclass_module, kwargs):
        # wrappedinstance  = wrappedclass_module(**kwargs) 
        # initialize the DelegateFunctionsMixin with the created wrapped object.

        wrappercore.BaseOptionsSetterMixin.optionsFromDict(self, kwargs)
        self.trained = False
            
    def get_params(self):
        return {
            "layer_count" : self.layer_count
        }
    
    def set_params(self, **parameterdict):
        if "layer_count" in parameterdict:
            self.layer_count = int(parameterdict["layer_count"])



    def create_nn(self):
        neuralnet = NeuralNet(self.layer_count, self.in_size, self.out_size)
        # print(f"created nn with: layer_count={self.layer_count}, in_size={self.in_size}, out_size={self.out_size}")
        if not self.trained:
            neuralnet.nn_create(load = False)
            # print("nn_create without loaded weights")
        else:
            # print("creating neural net with stats " + str(self.model_values))
            neuralnet.nn_create(load = True, weights_biases_values = self.model_values)
        return neuralnet

    def declare_classes(self, X):
        """ Declare the class labels to predict to.
        The first time this method only uniquely stores labels from X into a list.
        If declare_classes has been called before (self.classlables is assigned) this method only checks if the labels in X are all contained in the stored list. Else it will raise a value error.

        X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        if not hasattr(self, "classlabels"):
            self.classlabels = list(X["labels"]) # copy the labels into a new list
            # now delete multiple occurrences of a label
            # iterate over the list using index i1
            # delete every other entry with index i2 > i1 which has the same label
            # runtime is: O(n)
            i1 = 0 
            while i1 < len (self.classlabels): # len(X) is going to change in each iteration. so don't use a cached value.
                label = self.classlabels[i1]
                i1 += 1
                i2 = i1 # every index above i1 is looked at
                while i2 < len(self.classlabels):
                    if self.classlabels[i2] == label:
                        del(self.classlabels[i2])
                    else:
                        i2 += 1
        else: # declare_classes was called before.
            for label in X["labels"]:
                if label not in self.classlabels:
                    raise ValueError(f"{label} isn't contained in the declares classes set: {self.classlabels}")

        pass # method declare_classes end

    def train(self, X):
        """ Trains this neural network.

        X is a labeledinstances object for example: {"instances":[[1.0,2.0],[3.0,4.0]],"labels":["A","B"]}
        """
        
        if len(X["instances"]) == 0:
            # no training data was given..
            return # return doing nothing.

        self.declare_classes(X) # if declare classes was defined before checks if all labels are known.
        arffstruct = ArffStructure.from_labeledinstances(X, self.classlabels) # parse labeled instances



        if not self.trained:
            # set dimensions this is the first train call
            self.in_size = arffstruct.in_size
            self.out_size = arffstruct.out_size
        else:
            # check if input and output dimension match previous input and output dimension
            if self.in_size != arffstruct.in_size:
                # doesn't match previous train invocation
                raise ValueError(f"Dimension of the given labeledinstance is (in,out)=({arffstruct.in_size},{arffstruct.out_size} but the trained model only accepts (in,out)=({self.in_size},{self.out_size}).")

        # now train the neural net
        neuralnet = self.create_nn()
        self.model_values = neuralnet.nn_train(arffstruct = arffstruct)
        self.trained = True

    def predict(self, X):
        """ Does prediciton using the wrapped neural network based on input X.

        X is instances object for example: [[1.0,2.0,3.0],[4.0,5.0,6.0]]
        X may also be a dictionary object of labeledinstances. (Used when testing with labeledinstances)
        """
        if not self.trained:
            raise ValueError("This model hasn't been trained yet.")

        if not isinstance(X, dict):
            # wrap instances in a labeledinstances object with empty labels list
            X = {"instances": X, "labels": []}
        arffstruct = ArffStructure.from_labeledinstances(X, self.classlabels) # parse labeled instances

        if self.in_size != arffstruct.in_size:
            # doesn't match previous train invocation
            raise ValueError(f"Dimension of the given labeledinstance is (in,out)=({arffstruct.in_size},{arffstruct.out_size} but the trained model only accepts (in,out)=({self.in_size},{self.out_size}).")
        
        neuralnet = self.create_nn()
        prediction = neuralnet.nn_predict(arffstruct)
        dataobject = PASEDataObject("StringList", prediction)
        return dataobject

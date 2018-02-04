"""This package contains the code for parsing arff-data and using Tensorflow to handle neural networks.
    arff.py: library taken from: https://raw.githubusercontent.com/renatopp/liac-arff/
        It is used to parse arff-file content to python.
    arffcontainer.py: uses arff.py to parse the data into a fitting datastructure called ArffStruct ready to be fed to tensorflow variables.
    logger.py: Encapsulates a Result instance to make neural network operations visible for the client. For example: while training, the client can poll the result page over and over to watch the process.
    neuralnet.py: Contains the logic to setup, train and get predicitons from a neural net using the tensorflow framework.
"""
from .neuralnet import NeuralNet
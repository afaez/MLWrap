# used to test functionality of parsing arff files and neuralnetwork operations
import arffcontainer
import neuralnet
import arff
path = "arff_files/renatopp/arff-datasets/classification/zoo.arff"
struct = arffcontainer.parse(path)
if struct is None:
    print("struct empty")
    exit()
#print("intput matrix ", struct.input_matrix)
#print("output matrix ", struct.output_matrix)
net = neuralnet.NeuralNet()
net.nn_create(struct, 5, deviation = 0.5)
net.nn_train(struct, epochs = 5, load = False, learning_rate = 0.01, batch_size = 20)
#net.nn_predict(struct)
#net.nn_train(struct, epochs = 5, load = True, learning_rate = 0.01, batch_size = 20)
#net.nn_predict(struct)
#net.nn_train(struct, epochs = 5, load = True, learning_rate = 0.01, batch_size = 20)
#net.nn_predict(struct,path = "temp/cifar/cifar.ckpt")
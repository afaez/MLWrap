# used to test functionality of parsing arff files and neuralnetwork operations
import arffcontainer
import neuralnet
import arff
import pprint
path = "/Users/aminfaez/CrcTaskBasedConfigurator/testrsc/polychotomous/weather.arff"  # /Users/aminfaez/CrcTaskBasedConfigurator/testrsc/polychotomous#arff_files/renatopp/arff-datasets/classification/zoo.arff"
struct = arffcontainer.parse(path)
if struct is None:
    print("struct empty")
    exit()
#print("intput matrix ", struct.input_matrix)
#print("output matrix ", struct.output_matrix)
logs = []
net = neuralnet.NeuralNet(2,in_size=struct.in_size, out_size=struct.out_size, log=logs)
net.nn_create()

print(str(net.nn_train(struct)))
print(net.nn_predict(struct))
pp = pprint.PrettyPrinter(indent=4)
print("logs:")
pp.pprint(logs)
#net.nn_predict(struct)
#net.nn_train(struct, epochs = 5, load = True, learning_rate = 0.01, batch_size = 20)
#net.nn_predict(struct)
#net.nn_train(struct, epochs = 5, load = True, learning_rate = 0.01, batch_size = 20)
#net.nn_predict(struct,path = "temp/cifar/cifar.ckpt")
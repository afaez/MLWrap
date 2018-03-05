import tensorflow as tf
import math
import random
import logging
import numpy as np

class NeuralNet:
    """ Implements a tensorflow graph.  
    Args: 
        log: a nnhandler.logger.Logger instance. Messages will be written in it. see log function below. Note that the messages written to log will be saved in a models.Result instance and can be accessed through http get requests.
    Instance Attributes:
        x: tensorflow matrix variable representing the input layer of the net.
        y_: tensorflow matrix variable representing the output layer of the net.
        y: represents actual data outcome. taken from arff file. Used in training.
        cross_entropy: Tensorflow Neural Network Cross Entropy Error. Used for backpropagation when training.
        weights_biases_list: list of tensorflow variables to store the variables needed to use for checkpoints.
        _log: points to a Logger instance. Writes information about constrcution, training and prediction into the log.
    """
    def __init__(self, layers_count, in_size=0, out_size=0 , log = None):
        self._log = log
        self.in_size = in_size
        self.out_size = out_size
        self.layers_count = int(layers_count)


    def nn_create(self, deviation = 0.1, load = False, weights_biases_values = []):
        """ Creates the skeleton of the neural net.
        """
        tf.reset_default_graph() # reset old graph
        # declare the input data placeholders
        self.x = tf.placeholder(tf.float32, [None, self.in_size], name = "input_layer")
        # declare the output data placeholder
        self.y = tf.placeholder(tf.float32, [None, self.out_size], name = "output_layer")
        # empty list
        self.weights_biases_list = []

        # declare the weights and biases 
        # there will be layers_count-1 many hidden layers
        # each hidden layer contains the mean of in_size and out_size many nodes
        hidden_out = self.x # points to the output of last layer. In the first iteration prev_layer points to the input layer x.
        prev_nodes_count = self.in_size 
        # store how many nodes the layer in the last iteration had. Used for the length of the matrix.
        self.log("Construct a neuronal network:")           ##
        self.log(f"network: {self.layers_count} layers")         ## Wrinting information to log.
        self.log(f"input layer: {prev_nodes_count} nodes")  ##
        for hidden_index in range(0, self.layers_count-1):
            hidden_in = hidden_out
            # how many nodes to be used in this layer
            nodes_count = nodes_count_formula(self.layers_count, self.in_size, self.out_size, hidden_index)
            self.log(f"hidden layer {hidden_index}: {nodes_count} nodes")
            # We initialise the values of the weights using a random normal distribution with a mean of zero and a standard deviation of dev
            if load:
                # load weights and biases
                w_i = tf.Variable(weights_biases_values[hidden_index*2])
                b_i = tf.Variable(weights_biases_values[hidden_index*2+1])
            else:
                # weight matrix is a 2-dim sqaure matrix: (prev_nodes_count x nodes_count)
                w_i = tf.Variable(
                    tf.random_normal([prev_nodes_count, nodes_count], stddev = deviation),
                    name = f"weight{hidden_index}")
                # bias vector : (1 x nodes_count)
                b_i = tf.Variable(
                    tf.random_normal([nodes_count], stddev = deviation), 
                    name=f"bias{hidden_index}")
            self.weights_biases_list.append(w_i)
            self.weights_biases_list.append(b_i)
            # calculate the output of the hidden layer of this loop iteration
            hidden_out = tf.add(tf.matmul(hidden_in, w_i), b_i)
            hidden_out = tf.tanh(hidden_out, name = f"hidden{hidden_index}_out")
            prev_nodes_count = nodes_count
        self.log(f"output layer: {self.out_size} nodes")
        # now calculate the last hidden layer output - in this case, let's use a softmax activated
        # the weights connecting the last hidden layer to the output layer
        if load:
            # load weights and biases
            w_o = tf.Variable(weights_biases_values[-2])
            b_o = tf.Variable(weights_biases_values[-1])
        else:
            w_o = tf.Variable(tf.random_normal([prev_nodes_count, self.out_size], stddev = deviation), name='weightout')
            b_o = tf.Variable(tf.random_normal([self.out_size]), name='biasout')
        self.weights_biases_list.append(w_o)
        self.weights_biases_list.append(b_o)
        # output layer
        self.y_ = tf.nn.softmax(tf.add(tf.matmul(hidden_out, w_o), b_o))
        # clip outout.
        y_clipped = tf.clip_by_value(self.y_, 1e-10, 0.9999999)

        # calculate cross entropy error
        self.cross_entropy = -tf.reduce_mean(
            tf.reduce_sum(self.y * tf.log(y_clipped)
                            + (1 - self.y) * tf.log(1 - y_clipped),
                        axis=1), name = "cross_entropy")

        
        # self.sum_square = tf.reduce_sum(tf.square(self.y_ - self.y)) # Use minimize cross entropy instead
    # END OF CREATE FUNCITON

    def nn_train(self, arffstruct, epochs = 1000, learning_rate = 0.3, batch_size = 900):
        """ Trains the neural net with data from arffstruct, which is a arffcontainer.ArffStructur instance.
            load: boolean, if true, nn_train first restores the net weights and biases from previous checkpoint from the given path.
            path: path of the tensorflow checkpoint folder, to restore when load is True. Also used to store the net at the end of the training
            This implementation trains the network using the small-batch method. instances are packed into batches of size batch_size. The network is trained unsing these batches in a random order. All the data is gone through epochs many times.
        """

        init_op = tf.global_variables_initializer()
        # add an optimiser
        optimiser = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(self.cross_entropy)

        # define an accuracy assessment operation
        correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        # start the session
        with tf.Session() as sess:
            # initialise the variables
            sess.run(init_op)

            
            total_set_size = arffstruct.entry_size
            # create a shuffled batch order list
            if total_set_size < batch_size * 2 :
                batch_order = [0]
            else:
                batch_order = list(range(int(total_set_size/batch_size)))
            self.log(f"Starting Training with learning rate = {learning_rate} and batch size = {batch_size} for {epochs} many epochs.")
            for epoch in range(epochs):
                avg_cost = 0
                random.shuffle(batch_order) # shuffle the order in each epoch
                for i in batch_order:
                    batch_start = i * batch_size
                    batch_end = (i+1) * batch_size
                    if batch_end >  total_set_size:
                        batch_end = total_set_size
                    if batch_end - batch_start < 1:
                        continue;
                    _, c = sess.run([optimiser, self.cross_entropy], 
                                feed_dict={ self.x: arffstruct.input_matrix[batch_start:batch_end],
                                            self.y: arffstruct.output_matrix[batch_start:batch_end]})
                    avg_cost += c / total_set_size
                #self.log(f"Epoch {epoch+1}: cost = {avg_cost:.3f}")
            accuracy_result =sess.run(accuracy, feed_dict={self.x : arffstruct.input_matrix, self.y: arffstruct.output_matrix})
            self.log(f"finished training: accuracy:{accuracy_result}")

            # save the model
            weights_biases_values = []
            for var in self.weights_biases_list:
                weights_biases_values.append(var.eval())
            return weights_biases_values
            
    def nn_predict(self, arffstruct):
        """ Loads the network form the fiven folder. Runs the neural network with the given input from arffstruct, which is an ArffStructure instance. 
        """
        init_op = tf.global_variables_initializer()
        # start the session
        with tf.Session() as sess:
            # initialise the variables
            sess.run(init_op)
            
            
            total_set_size = arffstruct.entry_size
            #predict every instance
            feed_dict={ self.x: arffstruct.input_matrix  }
            # output is a list of a list. e.g. output[0] is a list of softmaxed output layer values.
            output = sess.run(self.y_, feed_dict)
            classification = [] # contains classification
            # run through output to decide which class has been classified by the neural net for each instance:
            for instance_output in output:
                max_index = 0 # index that was predicted
                for current_index in range(len(instance_output)):
                    instance_node = instance_output[current_index]
                    if instance_node > instance_output[max_index]:
                        max_index = current_index

                classification.append(arffstruct.class_list[max_index]) #resolve class name
            return classification



    def log(self, message):
        """ Appends the message string to the log. If there is no log instance, prints the retult.
        """
        if self._log is not None :
            self._log.append(message)
        else :
            logging.debug(message)
    def setlog(self, message):
        """ Replaces logs text with the message string. If there is no log instance, prints the retult.
        """
        if self._log is not None :
            self._log.replace(message)
        else :
            logging.debug(message)
        
def nodes_count_formula(layers_count, in_count, out_count, layer_index):
    """This function is called when constructing the neural net graph to calculate the amount of nodes in one layer with the index 'layer_index'.
    Returns the amount of nodes to be used for the given setup.
    Warning: altering this method will lead to constructing networks that won't be compatible with the checkpoints made before, leading to error when loading old data. 
    Note: this formula was developed heuristically to achieve small amount of nodes in each layer to save storage space when saving weights_biases_listmatrices and biases, while also perserving accurate predictions. 
    # Currently the amount of nodes in each layer is calculated using a linear function: (slight change to improve predicitons. See code below)
    #
    # f(x) = m * x + c 
    # x : layer_index
    # f(x) : nodex_count
    # m : gradient is calculated: (y2-y1)/(x2-x1), x1(first layer), y1 = in_count, x2(last layer), y2 = out_count
    # c : contant. is in_count.
    """
    return int((in_count + out_count) / 2)
    # m = ((math.sqrt(out_count) - math.sqrt(in_count)))/layers_count 
    # c = math.sqrt(in_count)
    # nodes_count = 2 * int((m * (layer_index+1)) + c + 0.5)  
    # return nodes_count 


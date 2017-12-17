import tensorflow as tf
import math
import random
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
    def __init__(self, log = None):
        self._log = log


    def nn_create(self, arffstruct, layers_count, deviation = 0.1):
        """ Creates the skeleton of the neural net.
        Args:
            arffstruct: Is a nnhandler.arffcontainer.ArffStructure. Stores arff data in a manner which can be used by tensorflow.
        """
        tf.reset_default_graph() # reset old graph
        # declare the input data placeholders
        self.x = tf.placeholder(tf.float32, [None, arffstruct.in_size], name = "input_layer")
        # declare the output data placeholder
        self.y = tf.placeholder(tf.float32, [None, arffstruct.out_size], name = "output_layer")
        # empty list
        self.weights_biases_list = []

        # declare the weights and biases 
        # there will be layers_count-1 many hidden layers
        # each hidden layer contains the mean of in_size and out_size many nodes
        hidden_out = self.x # points to the output of last layer. In the first iteration prev_layer points to the input layer x.
        prev_nodes_count = arffstruct.in_size 
        # store how many nodes the layer in the last iteration had. Used for the length of the matrix.
        self.log("Construct a neuronal network:")           ##
        self.log(f"network: {layers_count} layers")         ## Wrinting information to log.
        self.log(f"input layer: {prev_nodes_count} nodes")  ##
        for hidden_index in range(0, layers_count-1):
            hidden_in = hidden_out
            # how many nodes to be used in this layer
            nodes_count = nodes_count_formula(layers_count, arffstruct.in_size, arffstruct.out_size, hidden_index)
            self.log(f"hidden layer {hidden_index}: {nodes_count} nodes")
            # We initialise the values of the weights using a random normal distribution with a mean of zero and a standard deviation of dev
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
        self.log(f"output layer: {arffstruct.out_size} nodes")
        # now calculate the last hidden layer output - in this case, let's use a softmax activated
        # the weights connecting the last hidden layer to the output layer
        w_o = tf.Variable(tf.random_normal([prev_nodes_count, arffstruct.out_size], stddev = deviation), name='weightout')
        b_o = tf.Variable(tf.random_normal([arffstruct.out_size]), name='biasout')
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
        ##self.sum_square = tf.reduce_sum(tf.square(self.y_ - self.y)) # Use minimize cross entropy instead
    # END OF CREATE FUNCITON

    def nn_train(self, arffstruct, epochs = 3, learning_rate = 0.05, batch_size = 10, load = False, path = "temp"):
        """ Trains the neural net with data from arffstruct, which is a arffcontainer.ArffStructur instance.
            load: boolean, if true, nn_train first restores the net weights and biases from previous checkpoint from the given path.
            path: path of the tensorflow checkpoint folder, to restore when load is True. Also used to store the net at the end of the training
            This implementation trains the network using the small-batch method. instances are packed into batches of size batch_size. The network is trained unsing these batches in a random order. All the data is gone through epochs many times.
        """

        #create directory if it doesnt exist
        import os
        if not os.path.exists(path):
            os.makedirs(path)
        path += "/persistent.ckpt" # path now points to a checkpoint file
        # setup the initialisation operator
        init_op = tf.global_variables_initializer()

        #Add ops to save and restore all the variables stored in weights_biases_list.
        saver = tf.train.Saver(self.weights_biases_list)

        # add an optimiser
        optimiser = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(self.cross_entropy)

        # define an accuracy assessment operation
        correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        # start the session
        with tf.Session() as sess:
            # initialise the variables
            sess.run(init_op)
            if load :# 
                saver.restore(sess, path) # restore net if load  
                self.log("Model restored from checkpoint.")
            
            total_set_size = arffstruct.entry_size
            # create a shuffled batch order list
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
                self.log(f"Epoch {epoch+1}: cost = {avg_cost:.3f}")
            accuracy_result =sess.run(accuracy, feed_dict={self.x : arffstruct.input_matrix, self.y: arffstruct.output_matrix})
            self.log(f"accuracy:{accuracy_result}")
            save_path = saver.save(sess, path)
            self.log(f"Model saved in file: {save_path}")

    def nn_predict(self, arffstruct,  path = "temp"):
        """ Loads the network form the fiven folder. Runs the neural network with the given input from arffstruct, which is an ArffStructure instance. 
        """
        path += "/persistent.ckpt" # path now points to a checkpoint file
        # setup the initialisation operator
        init_op = tf.global_variables_initializer()

        # Add ops to save and restore all the variables stored in weights_biases_list.
        saver = tf.train.Saver(self.weights_biases_list)

        # start the session
        with tf.Session() as sess:
            # initialise the variables
            sess.run(init_op)
            saver.restore(sess, path) # restore net if load  
            print("Model restored.")
            
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
            import json
            self.setlog(json.dumps(classification))    



    def log(self, message):
        """ Appends the message string to the log. If there is no log instance, prints the retult.
        """
        if self._log is not None :
            self._log.append(message)
        else :
            print(message)
    def setlog(self, message):
        """ Replaces logs text with the message string. If there is no log instance, prints the retult.
        """
        if self._log is not None :
            self._log.replace(message)
        else :
            print(message)
        
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
    m = ((math.sqrt(out_count) - math.sqrt(in_count)))/layers_count 
    c = math.sqrt(in_count)
    nodes_count = 2 * int((m * (layer_index+1)) + c + 0.5)  
    return nodes_count 


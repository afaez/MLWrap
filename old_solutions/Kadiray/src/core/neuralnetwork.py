"""Neural Network class"""
import tensorflow as tf

import src.util.arffutil as arff


class NeuralNetwork:
    """Represents a neural network.

    Neural network can have variable number of layers. Training and test files are stored and read from the
    neural network's directory. Weight and Bias values of the neural network model is stored
    into the corresponding model directory after training. These values then will be restored to predict the
    output of prediction/test data.
    """

    def __init__(self, n_layers=None, model_directory=None, training_file_directory=None, test_file_directory=None):
        """Create a new NeuralNetwork object

        Args:
            n_layers: Number of layers of the neural network
            model_directory: Directory to save and restore the neural network values
            training_file_directory: Training file directory
            test_file_directory: Test file directory

        """
        self.model_directory = model_directory

        # initialize for training
        if training_file_directory is not None:
            self.data = arff.get_data(training_file_directory)
        # initialize for prediction
        elif test_file_directory is not None:
            self.data = arff.get_data(test_file_directory)

        # number of nodes for layers this can be parameterized in future
        self.n_nodes_in_layers = 200

        # number of input attributes
        self.n_attributes = arff.get_n_attributes(self.data)

        # number of output labels
        self.n_classes = arff.get_n_classes(self.data)

        # size of batch to process
        self.batch_size = 100

        # reseting default graph help accessing correct model variables
        tf.reset_default_graph()

        # placeholders for data and labels
        self.x = tf.placeholder(tf.float32, [None, self.n_attributes])
        self.y = tf.placeholder(tf.float32, [None, self.n_classes])

        # weights and biases for input_layer
        self.input_layer_weight_and_bias = {
            'weights': tf.Variable(tf.random_normal([self.n_attributes, self.n_nodes_in_layers])),
            'biases': tf.Variable(tf.random_normal([self.n_nodes_in_layers]))}

        self.weights_and_biases = []
        for i in range(n_layers):
            layer = {'weights': tf.Variable(tf.random_normal([self.n_nodes_in_layers, self.n_nodes_in_layers])),
                     'biases': tf.Variable(tf.random_normal([self.n_nodes_in_layers]))}
            self.weights_and_biases.append(layer)

        # weights and biases for output_layer
        self.output_layer = {'weights': tf.Variable(tf.random_normal([self.n_nodes_in_layers, self.n_classes])),
                             'biases': tf.Variable(tf.random_normal([self.n_classes]))}

    def neural_network_model(self, data):
        """Creates neural network model

        Args:
            data: data to run through the neural network

        Returns:
            output: tensor operation output
        """
        # operations for input layer
        hidden_layer = tf.add(tf.matmul(data, self.input_layer_weight_and_bias['weights']),
                              self.input_layer_weight_and_bias['biases'])
        hidden_layer = tf.nn.relu(hidden_layer)

        # operations for dynamic number of hidden layers
        for i in range(len(self.weights_and_biases)):
            hidden_layer = tf.add(tf.matmul(hidden_layer, self.weights_and_biases[i]['weights']),
                                  self.weights_and_biases[i]['biases'])
            hidden_layer = tf.nn.relu(hidden_layer)

        # operation for output
        output = tf.matmul(hidden_layer, self.output_layer['weights']) + self.output_layer['biases']

        return output

    def train_neural_network(self):
        """Runs training data through the neural network to optimize the model values

        """

        output = self.neural_network_model(self.x)
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=self.y))
        optimizer = tf.train.AdamOptimizer().minimize(cost)

        n_epochs = 10

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            for epoch in range(n_epochs):
                epoch_loss = 0
                batch_start = 0
                batch_end = self.batch_size
                num_training_examples = len(self.data['data'])
                for _ in range(int(num_training_examples / self.batch_size)):
                    batch_x = arff.get_batch_attributes(self.data, batch_start, batch_end, self.n_attributes)
                    batch_y = arff.get_batch_classes(self.data, batch_start, batch_end)
                    _, c = sess.run([optimizer, cost], feed_dict={self.x: batch_x, self.y: batch_y})
                    epoch_loss += c
                    batch_start += self.batch_size
                    batch_end += self.batch_size
                print('Epoch', epoch, 'of', n_epochs, 'loss:', epoch_loss)

            # save trained values to model directory
            tf.train.Saver().save(sess, self.model_directory)

    def predict(self):
        """Runs test data through the neural network model to have a prediction.

        Returns:
            predicted_labels: list of predicted class/label values for given test data
        """
        output = self.neural_network_model(self.x)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # restore trained values from model directory
            tf.train.Saver().restore(sess, self.model_directory)

            # prediction
            predictor = tf.argmax(output, 1)
            prediction_indexes = predictor.eval(
                feed_dict={
                    self.x: arff.get_batch_attributes(self.data, 0, len(self.data['data']),
                                                      self.n_attributes)}).tolist()

            # get one hot indexes and labels
            index_to_label = arff.one_hot_to_values()

            predicted_labels = []
            for i in prediction_indexes:
                predicted_labels.append(index_to_label[i])
            return predicted_labels

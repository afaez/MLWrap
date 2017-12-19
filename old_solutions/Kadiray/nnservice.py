"""Web Service End Points"""
from flask import Flask
from flask import request
from flask import jsonify
from src.core.neuralnetwork import NeuralNetwork
import uuid
import src.util.dbutil as dbutil
import os

app = Flask(__name__)

dbutil.init_db()


@app.route("/nn/create")
def create():
    """Accepts HTTP get parameter number_of_layers
       Creates a directory for the neural network, and inserts its definition into DB

    Returns:
        url: A hyper link to training function

    Example:
        HTTP GET /nn/create?number_of_layers=3
    """
    n_layer = request.args.get('number_of_layers')
    if n_layer is None:
        return "number_of_layers parameter must be sent", 400

    # generating a 10 character uuid to access the neural network
    nn_id = uuid.uuid4().hex[:10].upper()

    url = "/" + nn_id + "/train"

    directory = "./Data/nn/" + nn_id

    # insert into DB
    dbutil.insert_neural_network(nn_id, n_layer, directory)

    # create directory
    os.makedirs(directory, exist_ok=True)

    return "<a href=" + url + ">" + url + "</a>"


@app.route('/<nn_id>')
@app.route('/<nn_id>/train', methods=['POST'])
def train(nn_id):
    """Accepts an arff file to train the neural network

    Args:
        nn_id: Unique identifier to access the neural network

    Example:
        HTTP POST /D67AE901344/train
    """
    file = request.files['file']
    if file is not None:
        n_layers, directory = dbutil.get_neural_network(nn_id)

        if (n_layers is not None) and (directory is not None):
            file_save_directory = directory + "/train.arff"
            file.save(file_save_directory)

            nn_model_save_directory = directory + "/model.ckpt"

            nn = NeuralNetwork(n_layers, nn_model_save_directory, file_save_directory, None)
            nn.train_neural_network()

            # remove training file after training
            os.remove(file_save_directory)

            return "Training is done"
        else:
            return "Neural Network Not Found"
    else:
        return "Please send a train.arff file"


@app.route('/<nn_id>')
@app.route('/<nn_id>/predict', methods=['POST'])
def predict(nn_id):
    """Accepts an arff file to predict the class/label values

    Args:
        nn_id: Unique identifier to access the neural network

    Example: HTTP POST /D67AE901344/predict

    """
    file = request.files['file']
    if file is not None:
        n_layers, directory = dbutil.get_neural_network(nn_id)
        if (n_layers is not None) and (directory is not None):
            file_save_directory = directory + "/test.arff"
            file.save(file_save_directory)

            nn_model_save_directory = directory + "/model.ckpt"

            nn = NeuralNetwork(n_layers, nn_model_save_directory, None, file_save_directory)
            prediction = nn.predict()

            # delete test file after prediction
            os.remove(file_save_directory)
            return jsonify(predictions=prediction)
        else:
            return "Not Found"
    else:
        return "Please send a test.arff file "

app.run(debug=True)

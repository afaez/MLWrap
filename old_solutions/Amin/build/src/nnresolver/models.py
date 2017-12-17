"""Contains django models
"""
from django.db import models

class Nnentry(models.Model):
    """ Django model. Instances of this class are saved in a sql database.
    This class gives defines the columns of the network table and offers queries on the table.
    Attributes:
        id: Inherited from models.Model. Every instance has a unique id.
        state: Stores the state of the network. Can be Initialized, Assigned or Working. 
            INITIALIZED: If the network is initialized it has been created using "/nn/create" but hasnt been constructed yet. It is however ready to be trained using "/nn/train".
            ASSIGNED: If the network is initialized and is constructed using "/nn/train". In this state the net is ready to answer to "/nn/predict" or go through another training set using "/nn/train".
        working: If the network is being trained or is predicting at the moment. Concurrent access to networks isn't implemented yet so if one entry is set to be working then all access is prohibited.
        n: Integer. Stores the amount of layers in this neural network.
        size_input_layer: Integer. Stores the amount of nodes in the input layer. 
        size_output_layer: Integer. Stores the amount of nodes in the output layer.

    """
    INITIALIZED = 'IN' 
    ASSIGNED = 'AS' 
    NETWORK_STATE = (
        (INITIALIZED, 'Initialized'),
        (ASSIGNED, 'Assigned'),
    )
    state = models.CharField( 
        max_length=2,
        choices=NETWORK_STATE,
        default=INITIALIZED,
    )
    working = models.BooleanField(default=False)
    n = models.IntegerField()
    size_input_layer = models.IntegerField(null=True)
    size_output_layer = models.IntegerField(null=True)

    def exists(id_):
        """Checks if an entry with the given id exists.
        Return true if it does.
        """
        return Nnentry.objects.filter(id = id_).exists()

    def select(id_):
        """Returns the Nnentry instance from the DB with the given id_.
        """
        return Nnentry.objects.get(id = id_)

    def is_busy():
        """Returns false if there is one enty that has WORKING status.
        """
        return Nnentry.objects.filter(working = True).exists()

    def get_absolute_url(self):
        """ Override. 
        Returns: String that can be used to refer to the object over HTTP.
        """
        return f"/nn/{self.id}"  

    def path(self):
        """Returns the path as a string to the tensorflow checkpoint corresponding to the id.
        """
        return f"checkpoints/{self.id}"

    def __str__(self):
        return f"\n\tid: {self.id}\n\tlayers count: {self.n}\n\tnodes in input layer: {self.size_input_layer}\n\tnodes in output layer: {self.size_output_layer}"

    def clearworkers():
        """Class method. Sets every objects working status to false. Called once from module apps when starting up.
        """
        for entry in Nnentry.objects.filter(working = True):
            entry.working = False
            entry.save()

    def is_assigned(self):
        """Returns True, if this instance has been trained before. In this case a tensorflow checkpoint should be found at self.path(). 
        """
        return self.state == Nnentry.ASSIGNED

    def fits_in_out(self, input_size, output_size):
        """ Returns true if the entry has the same input output size.
        """
        if self.is_assigned(): # this network has been trained. So it will use a checkpoint. Check if checkpoint matches with the given input output size.
            return input_size == self.size_input_layer and output_size == self.size_output_layer
        else: # this network hasnt been trained so input and output size is not set yet.
            return True 
    
    def set_initialized(self, input_size, output_size):
        """ Initilizes this instance with the given parameters.
        """
        if not self.is_assigned(): # unassigned. set data and save.
            self.size_input_layer = input_size
            self.size_output_layer = output_size
            self.state = Nnentry.ASSIGNED
            self.save()



class Result(models.Model):
    """Result model. Each entry is a result page and is created for a corresponding request.
    Attributes:
        state: Stores if this is a result of train or predict.
        network: Foreignkey to the corresponding network.
        result_text: Result
        timestamp: Time and Date the request was made.
    """
    TRAIN = 'TR' 
    PREDICT = 'PR' 
    state = models.CharField( 
        max_length=2,
        choices=(
            (TRAIN, 'Training Result'),
            (PREDICT, 'Prediction Result'),),
        default=TRAIN,
    )
    network = models.ForeignKey(Nnentry, on_delete=models.CASCADE)
    result_text = models.TextField(default= "No result text has been set.")
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def exists(id_):
        """Checks if an entry with the given entry exists.
        Return true if there is.
        """
        return Result.objects.filter(id = id_).exists()
    def select(id_):
        """Returns the Result instance in the DB with the given id_.
        """
        return Result.objects.get(id = id_)
    def get_absolute_url(self):
        """ Override. 
        Returns: String that can be used to refer to the object over HTTP.
        """
        return f"/nn/result/{self.id}"  
    def __str__(self):
        return f"Result page for {self.state} request made at {self.timestamp}.\nCorresponding neuronal net:{self.network}\n\nResult text:\n{self.result_text}"

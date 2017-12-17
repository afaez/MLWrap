from django.shortcuts import  HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.http.request import QueryDict
from nnhandler import logger
from threading import Thread

@require_http_methods(["POST", "PUT"])
def operation(request, id_, training, training_dict = {}):
    """ Trains or lets the network make prediction using arff data from request.body.
    request.body has to contain a key 'data' mapping to arff-file content. 
    If request.method is POST: arff data can be encoded with form-data or x-www-form-urlencoded. (Tested with Postman)
    if request.method is PUT: arff data can only be encoded with x-www-form-urlencoded. (Tested with Postman)
    Params:
        request: http request. contains arff data in its body
        id_: Integer. identity number of the neural network to be trained.
        training: Boolean. True if this is a training operation
    Returns: 
        HttpResponse: responses with an error message if:
            0) The service is already working with tensorflow (training or predicting). Concurrent network access isnt supported yet.
            1) There is no network with the given id.
            2) request.body doesn't contain  valid arff data (See above). 
            3) The network hasn't been trained before and is now asked to predict.
        Else it returns a HttpRedirect to the result if the operation doesn't take longer than 5 seconds. Longer operations will return a HttpResponse which points to a status page, which can be polled.
        The status page is uniquely generated for each (/train or /predict) request and stores the result of each operation.
    """
    from nnresolver.models import Nnentry, Result
    # searching database for network with the given id_
    existence = Nnentry.exists(id_)
    if not existence: 
        # trying to access a network that wasn't initialized. Return with an error message
        return HttpResponse(f"Couldnt find neural net with id {id_}.")
    # searching databe for a network that is currently working.
    if Nnentry.is_busy():
        # Webservice is already using tensorflow to train or to predict. Try later again.
        return HttpResponse(f"Service is busy training or predicting. Try at another time again.")


    if request.method == 'POST':
        querydict = request.POST 
    elif request.method == 'PUT':
        querydict = QueryDict(request.body)


    # creating a models.Result instance. Save information about request.
    nn_entry = Nnentry.select(id_)
    result = Result(
                state = (Result.TRAIN if training else Result.PREDICT),
                network = nn_entry,
                result_text = "")
    result.save()
    if 'data' in querydict: 
        # arf-file content. django already decodes if it was encoded.
        arff_content = querydict['data'] 
    else :
        result.result_text = f"Error in request body: \n \n'data' key wasn't found"
        result.save()
        return HttpResponse("No arff data with a 'data' key was found in the body of the request.")

    if training :
        # start training on another thread.
        worker = Thread(target = worker_process,  args = (nn_entry,result,arff_content, True, training_dict))
    else :
        # start predicting on another thread.
        worker = Thread(target = worker_process,  args = (nn_entry,result,arff_content, False))

    worker.start()
    # wait 5 seconds for the operation to be completed.
    worker.join(5)
    # if worker is still working, point to a result page, which can be accessed to get status updates.
    redirection = not worker.isAlive()
    if redirection: # work is done. Redirect to result page:
        redirection_path = f"{result.get_absolute_url()}"
        if not training:
            #if predicting redirect to output of prediciton:
            redirection_path += "/out"  
        return redirect(redirection_path)
    else:
        #work is still in process. Point to the corresponding request page:
        urlpath = request.build_absolute_uri(result.get_absolute_url())
        return HttpResponse(f"Seems like the operation is going to take a while. To prevent a http-timeout, we have sent you this message after 5 seconds. \nYou can use the following URL to poll status updates: \n\t{urlpath} \nYou can also use the following link to access the output: \n\t{urlpath}/out")
    


def worker_process(nn_entry, result, arff_content, training, training_dict ={}):
    """ Operates on the network with the given entry using arff-content, which is a arff-file content as a string. 
    While operating, it continuously updates the result text. This function is given to a worker thread to be executed in the background.
    """
    nn_entry.working = True
    nn_entry.save()
    log = logger.Logger(result) # using log to update result
    try:
        # logic begins here:
        # if operation is predicting but neural net hasnt been trained before:  
        if not training and not nn_entry.is_assigned() :
            raise Exception("This neural network hasn't been trained before, so it cant answer to prediction requests.")

        #import neccesary moduls from nnhandler package
        from nnhandler import arffcontainer, neuralnet
        arffstruct = arffcontainer.parse(arff_content, is_path = False)
        if arffstruct is None:
            raise Exception("Error parsing arff-data.")
        else:
            log.append("Arff-data parsed successfully.")
        # create a neural net skeleton
        net = neuralnet.NeuralNet(log)
        if nn_entry.is_assigned and not nn_entry.fits_in_out(arffstruct.in_size, arffstruct.out_size):
            # this neural net has been trained before using a different arff layout. Checkpoint can be used. Return with error.
            raise Exception("Arff-data doesn't match previous training set.")
        # initialize tensorflow variables
        net.nn_create(arffstruct, nn_entry.n)
        # begin training
        path_ = nn_entry.path()
        load_ = nn_entry.is_assigned() # load only if network is assigned
        # based on the operation call train or predict:
        if training:
            net.nn_train(arffstruct, load = load_, path = path_, **training_dict)
        else :
            net.nn_predict(arffstruct, path = path_)
            
        nn_entry.set_initialized(arffstruct.in_size, arffstruct.out_size)
        # training has been completed
        if training:
            log.append("Training complete.")
    except Exception as e:
        log.append(f"Error while training: {e}")
    nn_entry.working = False
    nn_entry.save()
    pass
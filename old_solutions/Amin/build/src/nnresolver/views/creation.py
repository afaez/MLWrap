from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def create(request, n):
    """ Creates an neural network entry in the databse and responds with the url the databse can be accessed.
    """
    # create nn and get the id.
    entry = create_nn(n)
    # respond with the corresponding url pointing at the created nn.
    return respond_url(request, entry)


@require_http_methods(["GET", "POST"])
def extract_create(request):
    """ Extracts http parameters from GET and POST request and delegates the creation to create().
    """
    # A dictionary-like object containing all given HTTP GET parameters.
    if request.method == 'GET':
        querydict = request.GET
    elif request.method == 'POST':
        querydict = request.POST
    if 'n' in querydict: 
        # n defined in the header, extract parameter:
        n = querydict['n']
        # reuse other create function with the extracted n.
        return create(request, n)
    else :
        return HttpResponse(f"Couldn't extract parameter from : {request.path}.\n Try using a number instead. e.g.: /nn/create/6")

def respond_url(request, entry):
    """Creates a http responce pointing to the neural network entry.
    """
    urlpath = request.build_absolute_uri(entry.get_absolute_url())
    return HttpResponse(f"Created access to a new neural network with {entry.n} layers. It can be accessed through:\n\n\t{urlpath}/ \n \nPost http requests to {urlpath}/train together with arff-data as 'data' in the body of the request to train the network. Additionally,you can tune training parameters with following keywords in the body: 'epochs' = int, batch_size = int, learning_rate = float. \n \nAfterwards post {urlpath}/predict together with arff-data as 'data' in the body of the request to get a Json array as the prediction. \n \nNote that arff files with string or date attributes are not support.")


def create_nn(layercount):
    """Returns the created databse entry, referencing the neural net.
    The network iteself will be created when it is first being trained.
    """
    from nnresolver.models import Nnentry
    entry = Nnentry(n = layercount)
    entry.save()
    return entry

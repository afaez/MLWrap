from django.shortcuts import  HttpResponse
from django.views.decorators.http import require_http_methods
from django.http.request import QueryDict
from nnresolver.views import operate

@require_http_methods(["POST", "PUT"])
def train(request, id_):
    """This view resolves a training request, by extracting training parameters from the http request and delegating these to the Operation
    """
    # A dictionary-like object containing all given HTTP GET parameters.
    if request.method == 'POST':
        querydict = request.POST
    elif request.method == 'PUT':
        querydict = QueryDict(request.body)
    else:
        return HttpResponse("Use POST (prefedred) or PUT to train. ")
    # Filling in parameters:
    param_dict = {}
    try:
        if 'learning_rate' in querydict:
            param_dict['learning_rate'] = float(querydict['learning_rate'])
        if 'batch_size' in querydict:
            param_dict['batch_size'] = int(querydict['batch_size'])
        if 'epochs' in querydict:
            param_dict['epochs'] = int(querydict['epochs'])
    except Exception as e: 
        print(f"Couldnt parse training keys: {e}\n")
    return operate.operation(request, id_, True, param_dict)
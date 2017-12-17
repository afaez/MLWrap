from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods

def index(request):
    """ Returns an index page.
    """
    return HttpResponse(f"Hello. You're at the neural network resolver index.\n You can use /nn/create/6 to create a 6 layered neural network! \n \nYou used {request.build_absolute_uri()} to get here.")


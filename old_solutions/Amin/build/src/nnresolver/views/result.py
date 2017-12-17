"""Result view return result pages. These pages are saved in the database and stores indefenitly (unless the databse is erased)  
"""
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_http_methods

def get_result_page(request, id_):
    """ Displays detailed result page.
    """
    if not request.method == 'GET':
        return HttpResponse("Only GET requests are allowed.")
    from nnresolver.models import  Result
    # if result doesnt exist, return with an error:
    if not Result.exists(id_):
        return HttpResponse(f"There is no request with id = {id_}.")
    result = Result.select(id_) # Result instance
    return HttpResponse(f"URL:\n\t{request.build_absolute_uri()} \n----\n{result}")


def get_result_output(request, id_):
    """ Displays result output.
    """
    if not request.method == 'GET':
        return HttpResponse("Only GET requests are allowed.")
    # if result doesnt exist, return with an error:
    from nnresolver.models import  Result
    if not Result.exists(id_):
        return HttpResponse(f"There is no request with id = {id_}.")
    result = Result.select(id_) # Result instance
    return HttpResponse(result.result_text)

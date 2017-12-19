
from SL.models import Entry
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ResolverList(APIView):

    def get(self, request, format=None):
        """ Returns the list of every linear_regression type.
        """
        return Response("Hello World!")

    def post(self, request, format=None):
        pass 

class ResolverDetail(APIView):

    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass




""" Sets the name of the app and difines a method which is called once per startup.
"""
from django.apps import AppConfig
class NnresolverConfig(AppConfig):
    name = 'nnresolver'

    def ready(self):
        """Override. Is called once per server startup to cleanup unfinished tasks.
        """
        print("Neural Network request resolver is starting.")
        # importing model classes
        from nnresolver.models import Nnentry  
        # clear all wokring entries this the service is free to be used again.
        Nnentry.clearworkers()
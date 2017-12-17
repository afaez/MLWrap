"""nnresolver: neural network (request) resolver.
This package was generated using django startapp nnresolver.
It's main task is to resolve requests made by clients and give an http answer.
Main implementation moduls are:
    models.py: Contains django models to maintain a persistent site. From django's webpage:
        "A model is the single, definitive source of information about your data. It contains the essential fields and behaviors of the data you’re storing. Generally, each model maps to a single database table."
        In my implementation consists of two model classes: Nnentry (Neural network entry) and Result (Train or Prediction Result). 
    urls.py: Like in the nnws packge I delegate Http requests from clients using an urlpatterns list with regular expression. The requests are delegated to moduls in the views package. See views.__init__.py

"""
default_app_config = 'nnresolver.apps.NnresolverConfig'
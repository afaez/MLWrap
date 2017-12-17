from django.conf.urls import url
from django.contrib import admin
from .views import index, creation, operate, result, train

urlpatterns = [
    url(r'^create/([1-9][0-9]*)/?$', creation.create),       # create neural net
    url(r'^create/', creation.extract_create),               # extract param and create neural net
    url(r'^([0-9]+)/predict/?', operate.operation, {'training':False}), # predict
    url(r'^([0-9]+)/train/?', train.train),                         # train
    url(r'result/([0-9]+)/?$', result.get_result_page),             # result detailed
    url(r'result/([0-9]+)/out/?$', result.get_result_output),       # result output
    url(r'^.*$', index.index, name='index'),
]
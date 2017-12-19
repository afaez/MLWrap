from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from SL.linear_model import linear_regression


urlpatterns = [
    url(r'^LinearRegression/$', linear_regression.ResolverList.as_view()),
    url(r'^LinearRegression/(?P<pk>[0-9]+)/$', linear_regression.ResolverDetail.as_view()),
]
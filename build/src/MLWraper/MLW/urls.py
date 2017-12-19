"""MLW URL Configuration
"""
from django.conf.urls import include,url

urlpatterns = [
    url(r'^sl/', include('SL.urls')),
]

from django.conf.urls import include,url

urlpatterns = [
    url(r'^linear_model/', include('SL.linear_model.urls')),
]

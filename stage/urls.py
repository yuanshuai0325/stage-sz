from django.urls import path
from stage.views import add_device, search_device, add_use

urlpatterns = [
    path(r'adevice', add_device),
    path(r'sdevice', search_device),
    path(r'adduse', add_use),
]

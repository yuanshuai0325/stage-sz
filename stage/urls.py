from django.urls import path
from stage.views import add_device, sdevice, add_use, add_storage, search_device

urlpatterns = [
    path(r'adevice', add_device),
    path(r'sdevice', sdevice),
    path(r'adduse', add_use),
    path(r'addstorage', add_storage),
    path(r'searchdevice', search_device),
]

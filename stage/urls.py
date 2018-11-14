from django.urls import path
from stage.views import add_device, sdevice, add_use, add_storage, search_device, search_all_use, search_all_storage, update_device

urlpatterns = [
    path(r'adevice', add_device),
    path(r'sdevice', sdevice),
    path(r'adduse', add_use),
    path(r'addstorage', add_storage),
    path(r'searchdevice', search_device),
    path(r'searchalluse', search_all_use),
    path(r'searchallstorage', search_all_storage),
    path(r'updatedevice', update_device),
]

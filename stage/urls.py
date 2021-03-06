from django.urls import path
from stage.views import login, add_device, sdevice, add_use, add_storage, search_device, search_all_use, search_all_storage, update_device, update_use, update_storage, update_delete

urlpatterns = [
    path(r'login', login),
    path(r'adevice', add_device),
    path(r'sdevice', sdevice),
    path(r'adduse', add_use),
    path(r'addstorage', add_storage),
    path(r'searchdevice', search_device),
    path(r'searchalluse', search_all_use),
    path(r'searchallstorage', search_all_storage),
    path(r'updatedevice', update_device),
    path(r'updateuse', update_use),
    path(r'updatestorage', update_storage),
    path(r'updatedelete', update_delete),
]

from django.urls import path

from . import views
from app.views import index, exibir_empresa
urlpatterns = [
    path("", index, name='index'),
    path("exibirempresas", exibir_empresa)
]
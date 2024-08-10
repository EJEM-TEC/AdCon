from django.urls import path
from . import views

urlpatterns = [
    path("", index, name='index'),
    path("exibirempresas", exibir_empresa)
]
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from app import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login, name="login"),
    path("index", views.index, name="index"),
    path("exibirempresas", views.exibir_empresa, name="exibirempresas"),
    path("colaboradores", views.colaboradores, name="colaboradores"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("historico-transacoes.html", views.transacoes, name="transacoes"),
    path("perfil", views.perfil, name="perfil"),
    path("tributos", views.tributos, name="tributos"),
    path("404", views.page_404, name="page_404"),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as login_django
from django.contrib.auth.decorators import login_required
from rolepermissions.roles import assign_role
from rolepermissions.decorators import has_role_decorator
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

@login_required(login_url="/")
def exibir_empresa(request):
    return render(request, template_name="exemplo/exibir_empresa.html")

@login_required(login_url="/")
def index(request):
    return render(request, template_name="frontend/index.html")
def login(request):
    if request.user.is_authenticated:
        # Se o usuário já estiver autenticado, redirecione para a página inicial
        return redirect('index')

    if request.method == "GET":
        return render(request, 'frontend/pages-login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(username=username, password=senha)
        if user:
            login_django(request, user)
            return redirect('index')
        return HttpResponse("Usuário ou senha inválidos")
@login_required(login_url="/")
def transacoes(request):
    return render(request, template_name="frontend/pages-transacoes.html")

@login_required(login_url="/")
@has_role_decorator('administrador')
def colaboradores(request):
    if request.method == "GET":
        users = User.objects.all()
        return render(request, 'frontend/pages-colaboradores.html', {'users': users})
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        grupo = request.POST.get('grupo')

        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse("Já existe um usuário com esse nome")

        # Cria o novo usuário
        user = User.objects.create_user(username=username, email=email, password=senha)

        # Verifica se o grupo existe, se não, cria-o
        group, created = Group.objects.get_or_create(name=grupo)
        user.groups.add(group)
        # Salva o usuário
        user.save()
        assign_role(user, grupo)
        users = User.objects.all()
        return render(request, 'frontend/pages-colaboradores.html', {'users': users})
@login_required(login_url="/")
def perfil(request):
   return render(request, template_name="frontend/pages-perfil.html")

@login_required(login_url="/")
def tributos(request):
    return render(request, template_name="frontend/tributos.html")

@login_required(login_url="/")
def page_404(request):
    return render(request, template_name="frontend/pages-404.html")

def delete_user(request, user_id):
    context={}
    usuario=get_object_or_404(User, id=user_id)
    context['object']=usuario
    if request.method == "POST":
        usuario.delete()
        return redirect('colaboradores')
    return render(request, 'frontend/confirmar_excluir.html', context);
import random
from sqlite3 import IntegrityError
import random

from django.core.exceptions import ObjectDoesNotExist
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
from .models import Empresa, Federal, Estadual, Municipal, Tributo, FonteReceita, Vencimento, Criterios, EmpresaFonteReceita, EmpresaTributo, CriterioAliquotas


@login_required(login_url="/")
def exibir_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    cnpj = empresa.cnpj_federal.cnpj
    ie = empresa.ie_estadual.ie
    ccm = empresa.ccm_municipal.ccm

    print(ccm)  # Retorna o valor do ccm
    print(cnpj)  # Retorna o valor do cnpj
    print(ie)  # Retorna o valor do ie

    # Recuperando as instâncias relacionadas
    Cnpj = get_object_or_404(Federal, cnpj=cnpj)
    Ie = get_object_or_404(Estadual, ie=ie)
    Ccm = get_object_or_404(Municipal, ccm=ccm)
    return render(request, template_name="frontend/Empresa.html", context={
        "empresa":  empresa,
        "tributos": tributos,
        "Ccm": Ccm,
        "Ie": Ie,
        "Cnpj": Cnpj,
    })


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
    return render(request, template_name="frontend/historico-transacoes.html")


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
    return render(request, template_name="frontend/page-perfil.html")


@login_required(login_url="/")
def page_404(request):
    return render(request, template_name="frontend/pages-404.html")


def delete_user(request, user_id):
    context = {}
    usuario = get_object_or_404(User, id=user_id)
    context['object'] = usuario
    if request.method == "POST":
        usuario.delete()
        return redirect('colaboradores')
    return render(request, 'frontend/confirmar_excluir.html', context);


def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        grupo = request.POST.get('grupo')

        try:
            # Atualiza os campos do usuário
            user.username = username
            user.email = email

            # Apenas atualize a senha se for fornecida
            if senha:
                user.senha = senha

            # Adiciona o usuário ao grupo especificado
            group, created = Group.objects.get_or_create(name=grupo)
            user.groups.add(group)

            user.save()
            assign_role(user, grupo)

            return redirect('colaboradores')
        except IntegrityError:
            # Caso haja uma violação da restrição UNIQUE
            print("Ocorreu o IntegrityError")
            return render(request, 'frontend/pages-colboradores.html', {
                'user': user,
                'error_message': 'Nome de usuário ou email já está em uso.'
            })

    return render(request, 'frontend/Editar_Usuario.html', {'user': user})


@login_required(login_url="/")
def index(request):
    if request.method == 'POST':
        try:
            # Criação das entidades
            federal = Federal.objects.create(
                cnpj=request.POST.get('cnpj_federal'),
                login_federal=request.POST.get('login_federal'),
                senha_federal=request.POST.get('senha_federal'),
                certificado_digital_federal=bool(request.POST.get('certificado_digital_federal'))
            )

            estadual = Estadual.objects.create(
                ie=request.POST.get('ie_estadual'),
                login_estadual=request.POST.get('login_estadual'),
                senha_estadual=request.POST.get('senha_estadual'),
                certificado_digital_estadual=bool(request.POST.get('certificado_digital_estadual'))
            )

            municipal = Municipal.objects.create(
                ccm=request.POST.get('ccm_municipal'),
                login_municipal=request.POST.get('login_municipal'),
                senha_municipal=request.POST.get('senha_municipal'),
                certificado_digital_municipal=bool(request.POST.get('certificado_digital_municipal'))
            )

            empresa = Empresa.objects.create(
                nome=request.POST.get('nome_empresa'),
                responsaveis=request.POST.get('responsaveis_empresa'),
                atividade=request.POST.get('atividade_empresa'),
                regime_apuracao=request.POST.get('regime_apuracao'),
                cnpj_federal=federal,
                ie_estadual=estadual,
                ccm_municipal=municipal,
            )

            print("A empresa e as entidades relacionadas foram cadastradas com sucesso")
            return redirect('index')

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")
            return render(request, 'frontend/index.html', {'error_message': str(e)})

    empresas = Empresa.objects.all()
    return render(request, 'frontend/index.html', {'empresas': empresas})

@login_required(login_url="/")
def update_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Acessando os valores diretamente dos campos
    cnpj = empresa.cnpj_federal.cnpj
    ie = empresa.ie_estadual.ie
    ccm = empresa.ccm_municipal.ccm

    print(ccm)  # Retorna o valor do ccm
    print(cnpj)  # Retorna o valor do cnpj
    print(ie)  # Retorna o valor do ie

    # Recuperando as instâncias relacionadas
    Cnpj = get_object_or_404(Federal, cnpj=cnpj)
    Ie = get_object_or_404(Estadual, ie=ie)
    Ccm = get_object_or_404(Municipal, ccm=ccm)

    if request.method == "POST":
        try:
            # Atualizando os valores da instância Federal
            Cnpj.cnpj = request.POST.get('cnpj_federal')
            Cnpj.login_federal = request.POST.get('login_federal')
            Cnpj.senha_federal = request.POST.get('senha_federal')
            Cnpj.certificado_digital_federal = bool(request.POST.get('certificado_digital_federal'))
            Cnpj.save()

            # Atualizando os valores da instância Estadual
            Ie.ie = request.POST.get('ie_estadual')
            Ie.login_estadual = request.POST.get('login_estadual')
            Ie.senha_estadual = request.POST.get('senha_estadual')
            Ie.certificado_digital_estadual = bool(request.POST.get('certificado_digital_estadual'))
            Ie.save()

            # Atualizando os valores da instância Municipal
            Ccm.ccm = request.POST.get('ccm_municipal')
            Ccm.login_municipal = request.POST.get('login_municipal')
            Ccm.senha_municipal = request.POST.get('senha_municipal')
            Ccm.certificado_digital_municipal = bool(request.POST.get('certificado_digital_municipal'))
            Ccm.save()

            # Atualizando a instância Empresa
            empresa.nome = request.POST.get('nome_empresa')
            empresa.responsaveis = request.POST.get('responsaveis_empresa')
            empresa.atividade = request.POST.get('atividade_empresa')
            empresa.regime_apuracao = request.POST.get('regime_apuracao')
            empresa.cnpj_federal = Cnpj  # Atribuindo a instância, não apenas o valor do campo
            empresa.ccm_municipal = Ccm  # Atribuindo a instância, não apenas o valor do campo
            empresa.ie_estadual = Ie  # Atribuindo a instância, não apenas o valor do campo
            empresa.save()

            return redirect('index')
        except IntegrityError:
            print("Ocorreu o IntegrityError")

    return render(request, 'frontend/Editar_Empresa.html', {'empresa': empresa,
                                                            'municipal': Ccm,
                                                            'estadual': Ie,
                                                            'federal': Cnpj})

@login_required(login_url="/")
def delete_empresa(request, empresa_id):
    print("Função delete_empresa foi chamada.")
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Acessando os valores diretamente dos campos
    cnpj = empresa.cnpj_federal.cnpj
    ie = empresa.ie_estadual.ie
    ccm = empresa.ccm_municipal.ccm

    print(ccm)  # Retorna o valor do ccm
    print(cnpj)  # Retorna o valor do cnpj
    print(ie)  # Retorna o valor do ie

    # Recuperando as instâncias relacionadas
    Cnpj = get_object_or_404(Federal, cnpj=cnpj)
    Ie = get_object_or_404(Estadual, ie=ie)
    Ccm = get_object_or_404(Municipal, ccm=ccm)

    if request.method == 'POST':
        empresa.delete()
        Cnpj.delete()
        Ie.delete()
        Ccm.delete()
        return redirect('index')

    return render(request, 'frontend/excluir_empresa.html', {'empresa': empresa})

@login_required(login_url='/')
def update_perfil(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            # Atualiza os campos do usuário
            user.username = username
            user.email = email

            # Apenas atualize a senha se for fornecida
            if senha:
                user.senha = senha

            user.save()

            return redirect('index')
        except IntegrityError:
            # Caso haja uma violação da restrição UNIQUE
            print("Ocorreu o IntegrityError")

    return render(request, 'frontend/page-perfil.html', {'user': user})

@login_required(login_url='/')
def tributos(request):
    tributos = Tributo.objects.all()

    if request.method == 'POST':
        # Coletando dados do formulário manualmente
        nome_tributo = request.POST.get('nome')
        fonte_receita_id = request.POST.get('fonte_receita')
        dia_vencimento = request.POST.get('dia')
        periodo_pagamento = request.POST.get('periodo_pagamento')
        mes_vencimento = request.POST.get('mes')
        deducao_imposto = request.POST.get('deducao_imposto')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')


        # Criando Vencimento
        vencimento = Vencimento.objects.create(
            dia=dia_vencimento,
            periodo_pagamento=periodo_pagamento,
            mes=mes_vencimento
        )

        # Criando Criterios
        criterios = Criterios.objects.create(
            deducao_imposto=deducao_imposto,
            limite_superior=limite_superior,
            limite_inferior=limite_inferior,
            aliquota=aliquota
        )

        # Criando Tributo
        fonte_receita = FonteReceita.objects.get(id_fonte_receita=fonte_receita_id)
        tributo = Tributo.objects.create(
            nome=nome_tributo,
            id_data_vencimento_vencimento_id=vencimento.id_data_vencimento,
            id_fonte_receita_fonte_receita_id=fonte_receita.id_fonte_receita,
        )

        # Criando CriterioAliquotas
        CriterioAliquotas.objects.create(
            id_aliquotas_criterios_id=criterios.id_aliquotas,
            id_tributo_tributo_id=tributo.id_tributo
        )

        return redirect('tributos')  # Redirecione para uma página de sucesso

    fontes_receitas = FonteReceita.objects.all()
    return render(request, 'frontend/tributos.html',
                  {
                      "fontes_receita": fontes_receitas,
                      "tributos": tributos
                  })

@login_required(login_url='/')
def excluir_tributo(request, tributo_id):
    context = {}
    tributo = get_object_or_404(Tributo, id=tributo_id)
    context['object'] = tributo
    if request.method == 'POST':
        tributo.delete()
        return redirect('tributos')
    return render(request, 'frontend/excluir_tributo.html', context);



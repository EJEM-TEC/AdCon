from decimal import Decimal
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
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Empresa, Federal, Estadual, Municipal, EmpresaFonteReceita, FonteReceita, EmpresaTributo, Tributo, \
    EmpresaTransacoes, EmpresaSimples, ObrigacaoExtra, EmpresaObrigacao
from django.db.models import Sum
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import date
from django.db.models.functions import ExtractMonth, ExtractYear  # Import necessário
from django.db.models import Sum
from calendar import monthrange
from datetime import date, timedelta
import datetime
import json
from .models import Empresa, Federal, Estadual, Municipal, Tributo, FonteReceita, Vencimento, Criterios, \
    EmpresaFonteReceita, EmpresaTributo, CriterioAliquotas, EmpresaTransacoes, Transacoes, Observacoes, \
    EmpresaObservacao, \
    Historico, HistoricoEmpresa, DepartamentoDP, Empresa_DP, EmpresaDespesas, Despesas, SimplesNacional, Anexos, SimplesAnexo

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date


@login_required(login_url="/")
def exibir_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Recupera os IDs de CNPJ, IE e CCM da empresa
    cnpj = empresa.federal.id
    ie = empresa.estadual.id
    ccm = empresa.municipal.id

    # Recupera instâncias de Federal, Estadual e Municipal usando os IDs
    Cnpj = get_object_or_404(Federal, id=cnpj)
    Ie = get_object_or_404(Estadual, id=ie)
    Ccm = get_object_or_404(Municipal, id=ccm)

    # Fontes de Receita da Empresa
    empresa_fontesreceitas = EmpresaFonteReceita.objects.filter(id_empresa_empresa=empresa).select_related(
        'id_fonte_receita_fonte_receita')

    fontes_receitas = [efr.id_fonte_receita_fonte_receita for efr in empresa_fontesreceitas]

    # Tributos de uma empresa
    empresa_tributos = EmpresaTributo.objects.filter(id_empresa_empresa=empresa_id).select_related(
        'id_tributo_tributo'
    )
    tributos = [et.id_tributo_tributo for et in empresa_tributos]

    #Observações de uma empresa
    empresa_observacoes = EmpresaObservacao.objects.filter(id_empresa_empresa=empresa_id).select_related(
        'id_observacoes'
    )

    observacoes = [eo.id_observacoes for eo in empresa_observacoes]

    #Anexos de uma empresa -  Simples Nacional

    empresa_anexos = EmpresaSimples.objects.filter(id_empresa=empresa_id).select_related(
        'id_simples'
    )

    anexos = [ea.id_simples for ea in empresa_anexos]

    #Históricos de uma empresa
    empresa_historicos = HistoricoEmpresa.objects.filter(id_empresa_empresa=empresa_id).select_related(
        'id_historico'
    )

    historicos = [eh.id_historico for eh in empresa_historicos]

    #Dp de uma empresa
    empresa_dp = Empresa_DP.objects.filter(id_empresa_empresa=empresa_id).select_related(
        'id_dp_dp'
    )

    dps = [ed.id_dp_dp for ed in empresa_dp]

    #Obrigações de uma empresa
    empresa_obrigacoes = EmpresaObrigacao.objects.filter(id_empresa_empresa=empresa_id).select_related(
        'id_obrigacao'
    )

    obrigacoes = [eo.id_obrigacao for eo in empresa_obrigacoes]

    # Transações de uma empresa
    empresa_transacoes = EmpresaTransacoes.objects.filter(id_empresa_empresa=empresa).select_related(
        'id_transacoes_transacoes')

    transacoes = [et.id_transacoes_transacoes.transacao for et in empresa_transacoes]
    sum_transacoes = sum(transacoes)


    # Despesas de uma determianda empresa

    empresa_despesas = EmpresaDespesas.objects.filter(id_empresa_empresa=empresa).select_related('id_despesa_despesa')

    # Acessar o campo correto que contém o valor da despesa e somar
    despesas = [ed.id_despesa_despesa.despesa for ed in empresa_despesas]  # Supondo que 'valor' seja o campo correto
    sum_despesas = Decimal(sum(despesas))  # Somar os valores das despesas

    # Calculo do Lucro de uma empresa

    lucro = sum_transacoes - sum_despesas

    n_empresa_fontes_receita = empresa_fontesreceitas.count()
    n_empresa_tributos = empresa_tributos.count()

    # Somatória das transações agrupadas por mês do ano corrente
    transacoes_por_mes = EmpresaTransacoes.objects.filter(
        id_empresa_empresa=empresa,
        id_transacoes_transacoes__data__year=now().year
    ).annotate(
        mes=TruncMonth('id_transacoes_transacoes__data')
    ).values('mes').annotate(
        total_transacoes=Sum('id_transacoes_transacoes__transacao')
    ).order_by('mes')

    # Preparar dados para o gráfico ApexCharts
    meses = [t['mes'].strftime('%Y-%m') for t in transacoes_por_mes]  # Formato 'YYYY-MM' para representar o mês
    total_transacoes = [float(t['total_transacoes']) for t in transacoes_por_mes]

    # Convertendo os dados para JSON
    data_for_chart = json.dumps({
        'categories': meses,
        'series': total_transacoes
    })

    contextos = calcular_tributo_empresa(empresa_id);

    resultados_das = {}
    resultados_lucroPressumido = {}
    resultados_lucroReal = {}

    # Resultados Simples Nacional

    if empresa.regime_apuracao == "Simples Nacional":
        
        resultados_das = calcular_das_anual(empresa_id)

    if empresa.regime_apuracao == "Lucro Presumido":
        
        resultados_lucroPressumido = calcular_lucro_presumido_empresa(empresa_id)

    if empresa.regime_apuracao == "Lucro Real":
        
        resultados_lucroReal = calcular_lucro_real_empresa(empresa_id)

    print(resultados_lucroPressumido)
    

    return render(request, template_name="frontend/Empresa.html", context={
        "empresa": empresa,
        "tributos": tributos,
        "Ccm": Ccm,
        "Ie": Ie,
        "Cnpj": Cnpj,
        'fontes_receitas': fontes_receitas,
        'n_empresa_fontes_receita': n_empresa_fontes_receita,
        'n_empresa_tributos': n_empresa_tributos,
        'sum_transacoes': sum_transacoes,
        'data_for_chart': data_for_chart,  # Dados para o gráfico
        'contextos': contextos,
        'observacoes': observacoes,
        'historicos': historicos,
        'dps': dps,
        'lucro': lucro,
        'anexos': anexos,
        'resultados_das': resultados_das,
        'resultados_lucroPressumido': resultados_lucroPressumido,
        'resultados_lucroReal': resultados_lucroReal,
        'obrigacoes': obrigacoes,
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
        return render(request, "frontend/login_error.html")


@login_required(login_url="/")
def transacoes(request):
    return render(request, template_name="frontend/historico-transacoes.html")


@login_required(login_url="/")
#@has_role_decorator('administrador')
def colaboradores(request):

    if not request.user.groups.filter(name='administrador').exists() and not request.user.is_superuser:
        return render(request, 'frontend/not-permission.html')

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
            return render(request, 'frontend/error-page1.html')

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
def page_404(request, exception):
    return render(request, "frontend/pages-404.html", {}, status=404)


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

            # Atualiza os campos do usuário
            if username:
                user.username = username

            if email:
                user.email = email
            
            if senha:
                user.set_password(senha)
                
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
def criacao_empresa(request):
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
                federal=federal,
                estadual=estadual,
                municipal=municipal,
            )

            print("A empresa e as entidades relacionadas foram cadastradas com sucesso")
            return redirect('index')

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")
            return render(request, 'frontend/index.html', {'error_message': str(e)})

    return render(request, 'frontend/adicionar_empresa.html')


@login_required(login_url="/")
def update_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Acessando os valores diretamente dos campos
    cnpj = empresa.federal.id
    ie = empresa.estadual.id
    ccm = empresa.municipal.id

    print(ccm)  # Retorna o valor do ccm
    print(cnpj)  # Retorna o valor do cnpj
    print(ie)  # Retorna o valor do ie

    # Recuperando as instâncias relacionadas
    Cnpj = get_object_or_404(Federal, id=cnpj)
    Ie = get_object_or_404(Estadual, id=ie)
    Ccm = get_object_or_404(Municipal, id=ccm)

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
    cnpj = empresa.federal.id
    ie = empresa.estadual.id
    ccm = empresa.municipal.id

    print(ccm)  # Retorna o valor do ccm
    print(cnpj)  # Retorna o valor do cnpj
    print(ie)  # Retorna o valor do ie

    # Recuperando as instâncias relacionadas
    Cnpj = get_object_or_404(Federal, id=cnpj)
    Ie = get_object_or_404(Estadual, id=ie)
    Ccm = get_object_or_404(Municipal, id=ccm)

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
        envio_email = request.POST.get('envio_email')
        confirmar_email = request.POST.get('confirmar_email')
        periodo_pagamento = request.POST.get('periodo_pagamento')
        aliquota = request.POST.get('aliquota')
        regime = request.POST.get('regime')

        # Criando Vencimento
        vencimento = Vencimento.objects.create(
            dia=dia_vencimento,
            periodo_pagamento=periodo_pagamento,
        )


        # Criando Tributo
        fonte_receita = FonteReceita.objects.get(id_fonte_receita=fonte_receita_id)
        tributo = Tributo.objects.create(
            nome=nome_tributo,
            envio_email=envio_email,
            confirmacao_email=confirmar_email,
            aliquota = aliquota,
            regime = regime,
            id_data_vencimento_vencimento_id=vencimento.id_data_vencimento,
            id_fonte_receita_fonte_receita_id=fonte_receita.id_fonte_receita,
        )

        return redirect('tributos')  # Redirecione para uma página de sucesso

    fontes_receitas = FonteReceita.objects.all()
    tributos_mensais = Tributo.objects.filter(id_data_vencimento_vencimento__periodo_pagamento="Mensal").count()
    tributos_trimestral = Tributo.objects.filter(id_data_vencimento_vencimento__periodo_pagamento="Trimestral").count()


    return render(request, 'frontend/tributos.html',
                  {
                      "fontes_receita": fontes_receitas,
                      "tributos": tributos,
                      "tributos_mensais": tributos_mensais,
                      "tributos_trimestral": tributos_trimestral,
                  })


@login_required(login_url='/')
def excluir_tributo(request, tributo_id):
    context = {}
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)
    context['object'] = tributo
    if request.method == 'POST':
        tributo.delete()
        return redirect('tributos')
    return render(request, 'frontend/excluir_tributo.html', {'tributo': tributo});


@login_required(login_url='/')
def editar_tributo(request, tributo_id):
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)
    vencimento = get_object_or_404(Vencimento,
                                   id_data_vencimento=tributo.id_data_vencimento_vencimento.id_data_vencimento)
    fonte_receita = get_object_or_404(FonteReceita,
                                      id_fonte_receita=tributo.id_fonte_receita_fonte_receita.id_fonte_receita)

    if request.method == 'POST':
        # Coletando dados do formulário manualmente
        nome_tributo = request.POST.get('nome')
        periodo_pagamento = request.POST.get('periodo_pagamento')
        envio_email = request.POST.get('envio_email')
        confirmar_email = request.POST.get('confirmar_email')
        aliquota = request.POST.get('aliquota')
        regime = request.POST.get('request')
        fonte_receita_id = request.POST.get('fonte_receita')
        dia_vencimento = request.POST.get('dia')

        vencimento.dia = dia_vencimento
        vencimento.periodo_pagamento = periodo_pagamento
        tributo.nome = nome_tributo
        tributo.envio_email = envio_email
        tributo.aliquota = aliquota
        tributo.regime = regime
        tributo.confirmacao_email = confirmar_email
        fonte_receita.nome = fonte_receita_id

        tributo.save()

        return redirect('tributos')

    fontes_receitas = FonteReceita.objects.all()
    return render(request, 'frontend/editar_tributo.html', {'tributo': tributo,
                                                            'fontes_receita': fontes_receitas})


@login_required(login_url='/')
def criterios(request, tributo_id):
    # Obtendo o tributo pelo id_tributo fornecido
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)

    # Função para criar um novo critério em relação a um tributo
    if request.method == 'POST':
        # Coletando dados do formulário
        deducao_imposto = request.POST.get('deducao_imposto')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')

        # Criando um novo critério
        novo_criterio = Criterios.objects.create(
            deducao_imposto=deducao_imposto,
            limite_superior=limite_superior,
            limite_inferior=limite_inferior,
            aliquota=aliquota
        )

        # Relacionando o critério ao tributo
        CriterioAliquotas.objects.create(
            id_aliquotas_criterios=novo_criterio,  # Passando a instância de Criterios
            id_tributo_tributo=tributo  # Passando a instância de Tributo
        )

        # Redirecionando para a página de visualização de critérios
        return redirect('criterios', tributo_id=tributo.id_tributo)

    # Obtendo todos os CriterioAliquotas relacionados ao tributo
    criterio_aliquotas = CriterioAliquotas.objects.filter(id_tributo_tributo=tributo).select_related(
        'id_aliquotas_criterios')

    # Extraindo todos os critérios relacionados aos CriterioAliquotas
    criterios = [ca.id_aliquotas_criterios for ca in criterio_aliquotas]

    return render(request, 'frontend/criterios.html', {
        'tributo': tributo,
        'criterios': criterios
    })


@login_required(login_url='/')
def editar_criterio(request, tributo_id, criterio_id):
    # Obtendo o tributo pelo id_tributo fornecido
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    criterio = get_object_or_404(Criterios, id_aliquotas=criterio_id)

    if request.method == 'POST':
        deducao_imposto = request.POST.get('deducao_imposto')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')

        criterio.deducao_imposto = deducao_imposto
        criterio.limite_superior = limite_superior
        criterio.limite_inferior = limite_inferior
        criterio.aliquota = aliquota

        criterio.save()

        # Redirecionando para a página de visualização de critérios
        return redirect('criterios', tributo_id=tributo.id_tributo)

    return render(request, 'frontend/editar_criterio.html', {
        'tributo': tributo,
        'criterio': criterio
    })


@login_required(login_url='/')
def deletar_criterio(request, tributo_id, criterio_id):
    # Obtendo o tributo pelo id_tributo fornecido
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    criterio = get_object_or_404(Criterios, id_aliquotas=criterio_id)

    # Verificando se o critério está relacionado ao tributo
    criterio_aliquota = get_object_or_404(CriterioAliquotas, id_aliquotas_criterios=criterio,
                                          id_tributo_tributo=tributo)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        criterio_aliquota.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        criterio.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('criterios', tributo_id=tributo.id_tributo)

    return render(request, 'frontend/excluir_criterio.html', {
        'tributo': tributo,
        'criterio': criterio
    })


@login_required(login_url='/')
def fontes_receitas(request):
    fonte_receitas = FonteReceita.objects.all()

    if request.method == 'POST':
        fonte_receita_nome = request.POST.get('fonte_receita')

        FonteReceita.objects.create(nome=fonte_receita_nome)

        return redirect('fontes_receitas')

    return render(request, 'frontend/fonte_receitas.html', {'fonte_receitas': fonte_receitas})


@login_required(login_url='/')
def editar_fontes_receitas(request, fonte_receita_id):
    fonte_receita = get_object_or_404(FonteReceita, id_fonte_receita=fonte_receita_id)

    if request.method == 'POST':
        fonte_receita_nome = request.POST.get('fonte_receita')

        fonte_receita.nome = fonte_receita_nome
        fonte_receita.save()

        return redirect('fontes_receitas')

    return render(request, 'frontend/editar_fonte_receita.html', {'fonte_receita': fonte_receita})


@login_required(login_url='/')
def deletar_fontes_receitas(request, fonte_receita_id):
    fonte_receita = get_object_or_404(FonteReceita, id_fonte_receita=fonte_receita_id)

    if request.method == 'POST':
        fonte_receita.delete()
        return redirect('fontes_receitas')

    return render(request, 'frontend/excluir_fonte_receita.html', {'fonte_receita': fonte_receita})


@login_required(login_url='/')
def transacoes(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':
        data = request.POST.get('data')
        fonte_receita = request.POST.get('fonte_receita')
        valor = request.POST.get('valor')

        print(fonte_receita)

        # Criando um novo critério
        nova_transacao = Transacoes.objects.create(
            data=data,
            fonte_receita=fonte_receita,
            transacao=valor,
        )

        # Relacionando o critério ao tributo
        EmpresaTransacoes.objects.create(
            id_transacoes_transacoes=nova_transacao,  # Passando a instância de Criterios
            id_empresa_empresa=empresa  # Passando a instância de Tributo
        )

        return redirect('transacoes', empresa_id=empresa.id_empresa)

    # Obtendo todos os CriterioAliquotas relacionados ao tributo
    empresa_transacoes = EmpresaTransacoes.objects.filter(id_empresa_empresa=empresa).select_related(
        'id_transacoes_transacoes')

    # Extraindo todos os critérios relacionados aos CriterioAliquotas
    transacoes = [et.id_transacoes_transacoes for et in empresa_transacoes]

    fontes_receitas = FonteReceita.objects.filter(empresafontereceita__id_empresa_empresa=empresa)

    return render(request, 'frontend/historico-transacoes.html', {'transacoes': transacoes,
                                                                  'fontes_receitas': fontes_receitas,
                                                                  'empresa': empresa})


@login_required(login_url='/')
def deletar_transacao(request, empresa_id, transacao_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    transacao = get_object_or_404(Transacoes, id_transacoes=transacao_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_transacao = get_object_or_404(EmpresaTransacoes, id_transacoes_transacoes=transacao,
                                          id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_transacao.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        transacao.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('transacoes', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/excluir_transacao.html', {
        'empresa': empresa,
        'transacao': transacao
    })


@login_required(login_url='/')
def AssociarEmpresaFonteReceita(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    fontes_receitas = FonteReceita.objects.all()

    if request.method == 'POST':
        fonte_receita_id = request.POST.get('fonte_receita')
        fonte_receita = FonteReceita.objects.get(id_fonte_receita=fonte_receita_id)

        EmpresaFonteReceita.objects.create(
            id_empresa_empresa=empresa,
            id_fonte_receita_fonte_receita=fonte_receita,
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/associar_empresa_fontereceita.html', {
        'fontes_receitas': fontes_receitas,
        'empresa': empresa
    })


@login_required(login_url='/')
def DissociarEmpresaFonteReceita(request, empresa_id, fontereceita_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    fonte_receita = get_object_or_404(FonteReceita, id_fonte_receita=fontereceita_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_fontereceita = get_object_or_404(EmpresaFonteReceita, id_empresa_empresa=empresa,
                                             id_fonte_receita_fonte_receita=fonte_receita)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_fontereceita.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/des_empresa_fontereceita.html', {
        'fonte_receita': fonte_receita,
        'empresa': empresa
    })


@login_required(login_url='/')
def AssociarEmpresaTributo(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    tributos = Tributo.objects.all()

    if request.method == 'POST':
        tributo_id = request.POST.get('tributo')
        tributo = Tributo.objects.get(id_tributo=tributo_id)

        EmpresaTributo.objects.create(
            id_empresa_empresa=empresa,
            id_tributo_tributo=tributo,
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/associar_empresa_tributo.html', {
        'tributos': tributos,
        'empresa': empresa
    })


@login_required(login_url='/')
def DissociarEmpresaTributo(request, empresa_id, tributo_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    tributo = get_object_or_404(Tributo, id_tributo=tributo_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_tributo = get_object_or_404(EmpresaTributo, id_empresa_empresa=empresa,
                                        id_tributo_tributo=tributo)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_tributo.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/des_empresa_fontereceita.html', {
        'tributo': tributo,
        'empresa': empresa
    })


def index(request):
    nome = request.GET.get('nome')
    atividade = request.GET.get('atividade')
    responsavel = request.GET.get('responsavel')
    regime_apuracao = request.GET.get('regime_apuracao')

    empresas_lucro_real = Empresa.objects.filter(regime_apuracao='Lucro Real').count()
    empresas_simples_nacional = Empresa.objects.filter(regime_apuracao='Simples Nacional').count()
    empresas_lucro_presumido = Empresa.objects.filter(regime_apuracao='Lucro Presumido').count()

    # Inicializa a queryset com todas as empresas
    empresas = Empresa.objects.all()

    # Aplicando os filtros
    if nome:
        empresas = empresas.filter(nome__icontains=nome)

    if atividade:
        empresas = empresas.filter(atividade__icontains=atividade)

    if responsavel:
        empresas = empresas.filter(responsavel__icontains=responsavel)

    if regime_apuracao:
        empresas = empresas.filter(regime_apuracao=regime_apuracao)

    return render(request, 'frontend/index.html', {
        'empresas': empresas,
        'empresas_lucro_real': empresas_lucro_real,
        'empresas_simples_nacional': empresas_simples_nacional,
        'empresas_lucro_presumido': empresas_lucro_presumido
    })


def calcular_tributo_empresa(empresa_id):
    # Recuperar a empresa pelo ID
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Pegar todas as transações da empresa
    transacoes = Transacoes.objects.filter(empresatransacoes__id_empresa_empresa=empresa)

    tributo_contexts = []  # Lista para armazenar os dados de cada tributo
    detalhes_gerais = []  # Lista para armazenar os detalhes de todas as transações
    total_imposto_geral = 0
    total_deducao_geral = 0

    # Iterar sobre todos os tributos relacionados à empresa
    empresa_tributos = EmpresaTributo.objects.filter(id_empresa_empresa=empresa)

    for empresa_tributo in empresa_tributos:
        tributo = empresa_tributo.id_tributo_tributo

        # Inicializar totais por tributo
        total_imposto = 0
        total_deducao = 0
        detalhes = []

        # Iterar sobre todas as transações da empresa
        for transacao in transacoes:
            fonte_receita = transacao.fonte_receita
            valor_transacao = transacao.transacao

            # Verificar se a fonte de receita da transação coincide com o tributo
            if tributo.id_fonte_receita_fonte_receita.nome == fonte_receita:

                # Pegar todos os critérios de alíquota associados ao tributo que se aplicam ao valor da transação
                criterios_aliquota = CriterioAliquotas.objects.filter(
                    id_tributo_tributo=tributo,
                    id_aliquotas_criterios__limite_inferior__lte=valor_transacao,
                    id_aliquotas_criterios__limite_superior__gte=valor_transacao
                )

                # Iterar sobre todos os critérios aplicáveis
                for criterio_aliquota in criterios_aliquota:
                    aliquota = criterio_aliquota.id_aliquotas_criterios.aliquota / 100  # Dividir por 100 para obter a porcentagem
                    valor_calculado = valor_transacao * aliquota  # Calcular o valor baseado na alíquota

                    # Verificar se é imposto ou dedução
                    tipo = criterio_aliquota.id_aliquotas_criterios.deducao_imposto

                    if tipo == 'deducao':
                        total_deducao += valor_calculado
                    elif tipo == 'imposto':
                        total_imposto += valor_calculado

                    # Guardar os detalhes de cada transação e seus critérios aplicados
                    detalhes.append({
                        'transacao': transacao,
                        'tributo': tributo.nome,
                        'valor_calculado': valor_calculado,
                        'tipo': tipo,
                        'aliquota': criterio_aliquota.id_aliquotas_criterios.aliquota,
                        'limite_inferior': criterio_aliquota.id_aliquotas_criterios.limite_inferior,
                        'limite_superior': criterio_aliquota.id_aliquotas_criterios.limite_superior
                    })

        # Somatório dos valores de imposto e dedução por tributo
        total_a_pagar = total_imposto - total_deducao

        # Armazenar os dados para este tributo
        tributo_contexts.append({
            'tributo': tributo.nome,
            'detalhes': detalhes,
            'total_imposto': total_imposto,
            'total_deducao': total_deducao,
            'total_a_pagar': total_a_pagar,
        })

        # Adicionar os valores totais ao geral
        total_imposto_geral += total_imposto
        total_deducao_geral += total_deducao
        detalhes_gerais.extend(detalhes)

    total_a_pagar_geral = total_imposto_geral - total_deducao_geral

    context = {
        'empresa': empresa,
        'tributo_contexts': tributo_contexts,  # Contexto de cada tributo
        'detalhes_gerais': detalhes_gerais,  # Todos os detalhes de transações
        'total_imposto_geral': total_imposto_geral,
        'total_deducao_geral': total_deducao_geral,
        'total_a_pagar_geral': total_a_pagar_geral,
    }

    # Renderizar o template com os dados de todos os tributos e transações
    return context


@login_required(login_url='/')
def adicionarObservacao(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':
        observacao = request.POST.get("observacao")

        # Criando um novo critério
        nova_observacao = Observacoes.objects.create(
            observacao=observacao
        )

        # Relacionando o critério ao tributo
        EmpresaObservacao.objects.create(
            id_observacoes=nova_observacao,  # Passando a instância de Criterios
            id_empresa_empresa=empresa  # Passando a instância de Tributo
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/adicionar_observacao.html', {'empresa': empresa})


@login_required(login_url='/')
def deletarObservacao(request, empresa_id, observacao_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    observacao = get_object_or_404(Observacoes, id=observacao_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_observacao = get_object_or_404(EmpresaObservacao, id_observacoes=observacao,
                                           id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_observacao.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        observacao.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/deletar_observacao.html', {
        'empresa': empresa,
        'observacao': observacao
    })

@login_required(login_url='/')
def adicionarHistorico(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':
        data = request.POST.get("data")
        informacao = request.POST.get("informacao")

        # Criando um novo critério
        novo_historico = Historico.objects.create(
            data=data,
            informacao=informacao
        )

        # Relacionando o critério ao tributo
        HistoricoEmpresa.objects.create(
            id_historico=novo_historico,  # Passando a instância de Criterios
            id_empresa_empresa=empresa  # Passando a instância de Tributo
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/adicionar_historico.html', {'empresa': empresa})

@login_required(login_url='/')
def deletarHistorico(request, empresa_id, historico_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    historico = get_object_or_404(Historico, id=historico_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_historico = get_object_or_404(HistoricoEmpresa, id_historico=historico,
                                           id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_historico.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        historico.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/deletar_historico.html', {
        'empresa': empresa,
        'historico': historico
    })

@login_required(login_url='/')
def adicionarDP(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':

        data = request.POST.get("data")
        imposto = request.POST.get("imposto")
        valor = request.POST.get("valor")
        valor_juros = request.POST.get("valor_juros")
        local_pagamento = request.POST.get("local_pagamento")
        competencia =  request.POST.get("competencia")
        data_vencimento = request.POST.get("data_vencimento")

        novo_dp = DepartamentoDP.objects.create(
            data_pagamento=data,
            imposto = imposto,
            valor = valor,
            valor_com_juros = valor_juros,
            forma_envio = local_pagamento,
            confirmacao = 'Pendente',
            competencia = competencia,
            data_vencimento = data_vencimento
        )

        Empresa_DP.objects.create(
            id_dp_dp=novo_dp, 
            id_empresa_empresa=empresa 
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/adicionar_dp.html', {'empresa': empresa})

@login_required(login_url='/')
def editarDP(request, empresa_id, dp_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    dp = get_object_or_404(DepartamentoDP, id=dp_id)

    if request.method == 'POST':
        data = request.POST.get("data")
        imposto = request.POST.get("imposto")
        valor = request.POST.get("valor")
        valor_juros = request.POST.get("valor_juros")
        local_pagamento = request.POST.get("local_pagamento")
        confirmacao = request.POST.get("confirmacao")

        # Validação e formatação da data
        if data:
            try:
                dp.data_pagamento = parse_date(data)
                if dp.data_pagamento is None:
                    raise ValidationError("Data inválida")
            except ValidationError as e:
                return render(request, 'frontend/editar_dp.html', {
                    'empresa': empresa,
                    'dp': dp,
                    'error_message': f"Erro: {e}"
                })
        else:
            dp.data_pagamento = None  # ou defina um valor padrão, se necessário

        dp.imposto = imposto
        dp.valor = valor
        dp.valor_com_juros = valor_juros
        dp.forma_envio = local_pagamento
        dp.confirmacao = confirmacao

        dp.save()

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/editar_dp.html', {'empresa': empresa, 'dp': dp})

@login_required(login_url='/')
def deletarDP(request, empresa_id, dp_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    dp = get_object_or_404(DepartamentoDP, id=dp_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_dp = get_object_or_404(Empresa_DP, id_dp_dp=dp,
                                           id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_dp.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        dp.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/deletar_dp.html', {
        'empresa': empresa,
        'dp': dp
    })

@login_required(login_url='/')
def depesas(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':
        data = request.POST.get('data')
        motivo = request.POST.get('motivo')
        valor = request.POST.get('valor')


        # Criando um novo critério
        nova_despesa = Despesas.objects.create(
            data=data,
            motivo=motivo,
            despesa=valor,
        )

        # Relacionando o critério ao tributo
        EmpresaDespesas.objects.create(
            id_despesa_despesa=nova_despesa,  # Passando a instância de Criterios
            id_empresa_empresa=empresa  # Passando a instância de Tributo
        )

        return redirect('despesas', empresa_id=empresa.id_empresa)

    # Obtendo todos os CriterioAliquotas relacionados ao tributo
    empresa_despesas = EmpresaDespesas.objects.filter(id_empresa_empresa=empresa).select_related(
        'id_despesa_despesa')

    # Extraindo todos os critérios relacionados aos CriterioAliquotas
    despesas = [ed.id_despesa_despesa for ed in empresa_despesas]

    return render(request, 'frontend/historico-despesas.html', {'despesas': despesas,
                                                                  'empresa': empresa})

@login_required(login_url='/')
def deletar_despesa(request, empresa_id, despesa_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    despesa = get_object_or_404(Despesas, id=despesa_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_despesa = get_object_or_404(EmpresaDespesas, id_despesa_despesa=despesa,
                                          id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_despesa.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        despesa.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('despesas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/excluir_despesa.html', {
        'empresa': empresa,
        'despesa': despesa
    })

@login_required(login_url='/')
def simplesNacional(request):
    anexos = SimplesNacional.objects.all()

    if request.method == 'POST':
        # Coletando dados do formulário manualmente
        numero_anexo = request.POST.get('numero_anexo')
        tipo = request.POST.get('tipo')
        deducao = request.POST.get('deducao')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')

        # Criando Anexos
        anexo = Anexos.objects.create(
            deducao=deducao,
            limite_superior=limite_superior,
            limite_inferior=limite_inferior,
            aliquota=aliquota
        )

        simplesnacional = SimplesNacional.objects.create(
            numero_anexo=numero_anexo,
            tipo=tipo   
        )

        # Criando CriterioAliquotas
        SimplesAnexo.objects.create(
            id_simples=simplesnacional,
            id_anexo=anexo
        )

        return redirect('simplesNacional')  # Redirecione para uma página de sucesso
    
    return render(request, 'frontend/SimplesNacional.html',
                  {
                      "anexos": anexos,
                  })

@login_required(login_url='/')
def anexosCriterios(request, anexo_id):
    # Obtendo o tributo pelo id_tributo fornecido
    anexo = get_object_or_404(SimplesNacional, id=anexo_id)

    # Função para criar um novo critério em relação a um tributo
    if request.method == 'POST':
        # Coletando dados do formulário
        deducao = request.POST.get('deducao')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')

        # Criando um novo critério
        novo_criterio = Anexos.objects.create(
            deducao=deducao,
            limite_superior=limite_superior,
            limite_inferior=limite_inferior,
            aliquota=aliquota
        )

        # Relacionando o critério ao tributo
        SimplesAnexo.objects.create(
            id_anexo=novo_criterio,  # Passando a instância de Criterios
            id_simples=anexo  # Passando a instância de Tributo
        )

        # Redirecionando para a página de visualização de critérios
        return redirect('Anexocriterios', anexo_id=anexo.id)

    # Obtendo todos os CriterioAliquotas relacionados ao tributo
    simples_anexos = SimplesAnexo.objects.filter(id_simples=anexo).select_related(
        'id_anexo')

    # Extraindo todos os critérios relacionados aos CriterioAliquotas
    criterios = [ca.id_anexo for ca in simples_anexos]

    return render(request, 'frontend/anexoCriterios.html', {
        'anexo': anexo,
        'criterios': criterios
    })

@login_required(login_url='/')
def editar_anexoCriterio(request, anexo_id, criterio_id):
    # Obtendo o tributo pelo id_tributo fornecido
    anexo = get_object_or_404(SimplesNacional, id=anexo_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    criterio = get_object_or_404(Anexos, id=criterio_id)

    if request.method == 'POST':
        deducao = request.POST.get('deducao')
        limite_superior = request.POST.get('limite_superior')
        limite_inferior = request.POST.get('limite_inferior')
        aliquota = request.POST.get('aliquota')

        criterio.deducao = deducao
        criterio.limite_superior = limite_superior
        criterio.limite_inferior = limite_inferior
        criterio.aliquota = aliquota

        criterio.save()

        # Redirecionando para a página de visualização de critérios
        return redirect('Anexocriterios', anexo_id=anexo.id)

    return render(request, 'frontend/editar_anexoCriterio.html', {
        'anexo': anexo,
        'criterio': criterio
    })


@login_required(login_url='/')
def deletar_anexoCriterio(request, anexo_id, criterio_id):
    # Obtendo o tributo pelo id_tributo fornecido
    anexo = get_object_or_404(SimplesNacional, id=anexo_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    criterio = get_object_or_404(Anexos, id=criterio_id)

    # Verificando se o critério está relacionado ao tributo
    criterio_anexo = get_object_or_404(SimplesAnexo, id_simples=anexo,
                                          id_anexo=criterio)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        criterio_anexo.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        criterio.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('Anexocriterios', anexo_id=anexo.id)

    return render(request, 'frontend/excluir_anexoCriterio.html', {
        'anexo': anexo,
        'criterio': criterio
    })

@login_required(login_url='/')
def deletar_Anexo(request, anexo_id):
    context = {}
    anexo = get_object_or_404(SimplesNacional, id=anexo_id)
    context['object'] = anexo
    if request.method == 'POST':
        anexo.delete()
        return redirect('simplesNacional')
    return render(request, 'frontend/excluir_anexo.html', {'anexo': anexo});


@login_required(login_url='/')
def detalhes_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    anexos = empresa.anexos.all()  # Pega todos os anexos associados à empresa
    return render(request, 'detalhes_empresa.html', {'empresa': empresa, 'anexos': anexos})

@login_required(login_url='/')
def AssociarAnexoEmpresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    anexos = SimplesNacional.objects.all()

    if request.method == 'POST':
        anexos_id = request.POST.get('anexos')
        anexo = SimplesNacional.objects.get(id=anexos_id)

        EmpresaSimples.objects.create(
            id_empresa=empresa,
            id_simples=anexo,
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/associar_empresa_anexo.html', {
        'anexos': anexos,
        'empresa': empresa
    })
    


@login_required(login_url='/')
def DissociarAnexoEmpresa(request, empresa_id, anexo_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    anexo = get_object_or_404(SimplesNacional, id=anexo_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_anexo = get_object_or_404(EmpresaSimples, id_empresa=empresa,
                                        id_simples=anexo)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_anexo.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/des_empresa_anexo.html', {
        'anexo': anexo,
        'empresa': empresa
    })


def calcular_das_anual(empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Capturar os anexos da empresa
    empresa_anexos = EmpresaSimples.objects.filter(id_empresa=empresa).select_related('id_simples')
    anexos_relacionados = SimplesAnexo.objects.filter(
        id_simples__in=[ea.id_simples for ea in empresa_anexos]
    ).select_related('id_anexo')

    # Obter os meses disponíveis com transações
    meses_disponiveis = EmpresaTransacoes.objects.filter(
        id_empresa_empresa=empresa
    ).annotate(
        ano=ExtractYear('id_transacoes_transacoes__data'),
        mes=ExtractMonth('id_transacoes_transacoes__data')
    ).values('ano', 'mes').distinct().order_by('ano', 'mes')

    resultados = []

    # Iterar pelos meses e calcular períodos de 12 meses consecutivos
    for i in range(len(meses_disponiveis) - 11):  # Garantir pelo menos 12 meses disponíveis
        ano_inicio = meses_disponiveis[i]['ano']
        mes_inicio = meses_disponiveis[i]['mes']
        inicio_periodo = date(year=ano_inicio, month=mes_inicio, day=1)

        # Definir o final do período corretamente (último dia do mês 12 meses depois)
        ano_fim = meses_disponiveis[i + 11]['ano']
        mes_fim = meses_disponiveis[i + 11]['mes']
        fim_periodo = date(year=ano_fim, month=mes_fim, day=1) + timedelta(days=31)
        fim_periodo = fim_periodo.replace(day=1) - timedelta(days=1)  # Último dia do mês correto


        # Para obter o próximo mês após o `fim_periodo`
        proximo_mes = fim_periodo.month + 1
        ano_proximo = fim_periodo.year

        # Se for dezembro, devemos ajustar para janeiro do próximo ano
        if proximo_mes > 12:
            proximo_mes = 1
            ano_proximo += 1

        print(f"Próximo mês: {proximo_mes}/{ano_proximo}")


        # Verificar se há dados de todos os 12 meses no período
        meses_faturamento = EmpresaTransacoes.objects.filter(
            id_empresa_empresa=empresa,
            id_transacoes_transacoes__data__gte=inicio_periodo,
            id_transacoes_transacoes__data__lte=fim_periodo
        ).annotate(
            mes=ExtractMonth('id_transacoes_transacoes__data'),
            ano=ExtractYear('id_transacoes_transacoes__data')
        ).values('ano', 'mes').distinct()

        if len(meses_faturamento) < 12:
            continue  # Ignorar períodos incompletos

        # Calcular o faturamento anual
        transacoes = EmpresaTransacoes.objects.filter(
            id_empresa_empresa=empresa,
            id_transacoes_transacoes__data__gte=inicio_periodo,
            id_transacoes_transacoes__data__lte=fim_periodo
        ).aggregate(faturamento_anual=Sum('id_transacoes_transacoes__transacao'))

        faturamento_anual = Decimal(transacoes['faturamento_anual'] or 0)
        deducao_total = Decimal(0)
        imposto_total = Decimal(0)

        # Calcular imposto e deduções
        for relacao in anexos_relacionados:
            anexo = relacao.id_anexo
            if anexo.limite_inferior <= faturamento_anual <= anexo.limite_superior:
                aliquota = Decimal(anexo.aliquota) / Decimal(100)
                deducao = Decimal(anexo.deducao)
                valor_calculado = (faturamento_anual * aliquota) - deducao

                imposto_total += max(Decimal(0), valor_calculado)
                deducao_total += deducao

        
        resultados_mes = calcular_receita_bruta_mes(empresa_id)
        receita_mes = resultados_mes['receita_mes']
        aliquota_real = round((((faturamento_anual * anexo.aliquota / 100) - deducao_total) / faturamento_anual), 4) * 100

        # Obter o mês atual
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year

        if mes_atual == proximo_mes and ano_atual == ano_proximo:

            # Adicionar resultado do período
            resultados.append({
                'periodo': f"{inicio_periodo.strftime('%b/%Y')} - {fim_periodo.strftime('%b/%Y')}",
                'aliquota': anexo.aliquota,
                'faturamento_anual': faturamento_anual,
                'imposto_total': round(imposto_total, 2),
                'aliquota_real': aliquota_real,
                'receita_mes' : receita_mes,
                'mes' : resultados_mes['mes_atual'],
                'deducao_total': round(deducao_total, 2),
                'valor_pagamento': receita_mes * (aliquota_real / 100),
            })

    context = {
        'empresa': empresa,
        'resultados': resultados,
    }

    return context
def calcular_valor_imposto(base_calculo, aliquota, regime):
    """
    Função auxiliar para calcular o valor do imposto com base no regime e na alíquota.
    """
    if regime == 'mensal':
        return base_calculo * aliquota / 3  # Exemplo para dividir por 3 para regime mensal
    elif regime == 'trimestral':
        return base_calculo * aliquota  # Trimestral já considera o valor cheio
    return 0

def obter_percentual_lucro_presumido(area_atuacao):
    """
    Retorna o percentual de lucro presumido com base na área de atuação da empresa.
    """
    percentual_por_area = {
        'comercio': 0.08,
        'industria': 0.08,
        'prestacao_servicos': 0.32,
        'transporte_de_carga': 0.16,
        'serviços_medicos': 0.016,
        'atividades_hospitalares': 0.016,
        # Adicione outras áreas conforme necessário
    }
    return percentual_por_area.get(area_atuacao, 0.08)  # Default para evitar erro

def calcular_lucro_presumido_empresa(empresa_id, mes=None, ano=None):
    """
    Calcula o lucro presumido de uma empresa com base no faturamento mensal ou trimestral,
    podendo filtrar por mês e ano específicos.
    """
    # Recuperar a empresa pelo ID
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Recuperar os tributos vinculados à empresa através do modelo EmpresaTributo
    empresa_tributos = EmpresaTributo.objects.filter(id_empresa_empresa=empresa).select_related('id_tributo_tributo')

    empresa_tributos = [et.id_tributo_tributo for et in empresa_tributos]

    # Obter o percentual de lucro presumido com base na área de atuação
    area_atuacao = empresa.atividade
    percentual_lucro_presumido = obter_percentual_lucro_presumido(area_atuacao)

    print("Percentual de lucro presumido:", percentual_lucro_presumido)

    # Recuperar os anos em que a empresa tem transações (faturamento)
    transacoes = Transacoes.objects.filter(empresatransacoes__id_empresa_empresa=empresa)

   # Recuperar as transações (faturamento) da empresa
    transacoes = Transacoes.objects.filter(empresatransacoes__id_empresa_empresa=empresa)

    # Inicializar despesas como queryset vazio ou com dados da empresa
    despesas = Despesas.objects.filter(empresadespesas__id_empresa_empresa=empresa)

    # Aplicar filtro de ano, se fornecido
    if ano:
        transacoes = transacoes.filter(data__year=ano)
        despesas = despesas.filter(data__year=ano)

    # Aplicar filtro de mês, se fornecido
    if mes:
        transacoes = transacoes.filter(data__month=mes)
        despesas = despesas.filter(data__month=mes)

    
    anos_com_faturamento = transacoes.annotate(ano=ExtractYear('data')).values_list('ano', flat=True).distinct()

    print("Anos com faturamento:", anos_com_faturamento)

    contextos = []
    
    # Loop pelos anos com faturamento ou pelo ano filtrado
    for ano_faturamento in anos_com_faturamento:
        # Se um mês for fornecido, fazer o loop apenas por aquele mês
        meses = [mes] if mes else range(1, 13)  # Loop por todos os meses se não houver filtro de mês
        
        for mes_faturamento in meses:
            # Recuperar o faturamento da empresa para o mês específico
            faturamento_mensal = transacoes.filter(
                data__year=ano_faturamento,
                data__month=mes_faturamento
            ).aggregate(total=Sum('transacao'))['total'] or 0  # Faturamento mensal

            if faturamento_mensal == 0:
                continue  # Pular meses sem faturamento

            # Calcular a base de cálculo do lucro presumido para o mês
            base_calculo_mensal = float(faturamento_mensal) * percentual_lucro_presumido
            print("Base de cálculo:" , base_calculo_mensal)

            # Processar cada tributo vinculado à empresa
            for empresa_tributo in empresa_tributos:
                aliquota = empresa_tributo.aliquota / 100  # Converter para decimal
                vencimento = empresa_tributo.id_data_vencimento_vencimento.dia  # Acessar o campo de vencimento da ForeignKey

                # Calcular o imposto mensal
                if empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento == 'mensal':
                    valor_imposto = calcular_valor_imposto(base_calculo_mensal, aliquota, empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento)
                    print('Valor do imposto:', valor_imposto)
                    contexto = {
                        'empresa': empresa.nome,
                        'faturamento': faturamento_mensal,
                        'base_calculo': base_calculo_mensal,
                        'imposto': empresa_tributo.nome,
                        'aliquota': empresa_tributo.aliquota,
                        'valor_imposto': valor_imposto,
                        'valor_pagamento': valor_imposto,
                        'vencimento': vencimento,
                        'regime': empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento,
                        'mes_ano': f"{int(mes_faturamento):02d}/{int(ano_faturamento)}",
                        'fonte_receita': empresa_tributo.id_fonte_receita_fonte_receita.nome  # Acessar a fonte de receita
                    }
                    contextos.append(contexto)

                # Calcular o imposto trimestral (somar o faturamento a cada três meses)
                elif empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento == 'trimestral' and int(mes_faturamento) % 3 == 0:
                    faturamento_trimestral = 0
                    for m in range(int(mes_faturamento)-2, int(mes_faturamento)+1):  # Somar o faturamento dos três meses
                        faturamento_trimestral += transacoes.filter(
                            data__year=ano_faturamento,
                            data__month=m
                        ).aggregate(total=Sum('transacao'))['total'] or 0
                    
                    base_calculo_trimestral = float(faturamento_trimestral) * percentual_lucro_presumido
                    valor_imposto = calcular_valor_imposto(base_calculo_trimestral, aliquota, empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento)

                    contexto = {
                        'empresa': empresa.nome,
                        'faturamento': faturamento_trimestral,
                        'base_calculo': base_calculo_trimestral,
                        'imposto': empresa_tributo.nome,
                        'aliquota': empresa_tributo.aliquota,
                        'valor_imposto': valor_imposto,
                        'valor_pagamento': valor_imposto,
                        'vencimento': vencimento,
                        'regime': empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento,
                        'trimestre_ano': f"{(int(mes_faturamento)-2):02d}-{int(mes_faturamento):02d}/{ano_faturamento}",
                        'fonte_receita': empresa_tributo.id_fonte_receita_fonte_receita.nome  # Acessar a fonte de receita
                    }
                    contextos.append(contexto)

    return contextos


def calcular_lucro_real_empresa(empresa_id, mes=None, ano=None):
    """
    Calcula o lucro real de uma empresa com base no faturamento e nas despesas mensais ou trimestrais,
    podendo filtrar por mês e ano específicos.
    """
    # Recuperar a empresa pelo ID
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Recuperar os tributos vinculados à empresa através do modelo EmpresaTributo
    empresa_tributos = EmpresaTributo.objects.filter(id_empresa_empresa=empresa).select_related('id_tributo_tributo')
    empresa_tributos = [et.id_tributo_tributo for et in empresa_tributos]

    # Recuperar as transações (faturamento) da empresa
    transacoes = Transacoes.objects.filter(empresatransacoes__id_empresa_empresa=empresa)

    # Inicializar despesas como queryset vazio ou com dados da empresa
    despesas = Despesas.objects.filter(empresadespesas__id_empresa_empresa=empresa)

    # Aplicar filtro de ano, se fornecido
    if ano:
        transacoes = transacoes.filter(data__year=ano)
        despesas = despesas.filter(data__year=ano)

    # Aplicar filtro de mês, se fornecido
    if mes:
        transacoes = transacoes.filter(data__month=mes)
        despesas = despesas.filter(data__month=mes)

    # Recuperar os anos com faturamento ou o ano específico
    anos_com_faturamento = transacoes.annotate(ano=ExtractYear('data')).values_list('ano', flat=True).distinct()

    contextos = []
    
    # Loop por cada ano com faturamento registrado ou ano filtrado
    for ano_faturamento in anos_com_faturamento:
        # Se um mês for fornecido, fazer o loop apenas por aquele mês
        meses = [mes] if mes else range(1, 13)  # Loop por todos os meses se não houver filtro de mês

        for mes_faturamento in meses:
            # Recuperar o faturamento da empresa para o mês específico
            faturamento_mensal = transacoes.filter(
                data__year=ano_faturamento,
                data__month=mes_faturamento
            ).aggregate(total=Sum('transacao'))['total'] or 0  # Faturamento mensal

            # Converter faturamento para Decimal
            faturamento_mensal = Decimal(faturamento_mensal)

            # Recuperar as despesas da empresa para o mês específico
            despesas_mensais = despesas.filter(
                data__year=ano_faturamento,
                data__month=mes_faturamento
            ).aggregate(total=Sum('despesa'))['total'] or 0  # Despesas mensais

            # Converter despesas para Decimal
            despesas_mensais = Decimal(despesas_mensais)

            if faturamento_mensal == 0 and despesas_mensais == 0:
                continue  # Pular meses sem movimentação

            # Calcular o lucro real para o mês
            lucro_real_mensal = faturamento_mensal - despesas_mensais

            # Verificar tributos trimestrais
            for empresa_tributo in empresa_tributos:
                aliquota = Decimal(empresa_tributo.aliquota) / Decimal(100)  # Converter alíquota para decimal

                # Calcular o imposto mensal com base no lucro real
                if empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento == 'mensal':
                    if lucro_real_mensal > 0:
                        valor_imposto = calcular_valor_imposto(lucro_real_mensal, aliquota, 'mensal')
                        contexto = {
                            'empresa': empresa.nome,
                            'faturamento': faturamento_mensal,
                            'despesas': despesas_mensais,
                            'lucro_real': lucro_real_mensal,
                            'imposto': empresa_tributo.nome,
                            'aliquota': empresa_tributo.aliquota,
                            'valor_imposto': valor_imposto,
                            'valor_pagamento': valor_imposto,
                            'vencimento': empresa_tributo.id_data_vencimento_vencimento.dia,
                            'regime': 'mensal',
                            'mes_ano': f"{int(mes_faturamento):02d}/{int(ano_faturamento)}",
                            'fonte_receita': empresa_tributo.id_fonte_receita_fonte_receita.nome
                        }
                        contextos.append(contexto)

                # Calcular o imposto trimestral
                elif empresa_tributo.id_data_vencimento_vencimento.periodo_pagamento == 'trimestral' and mes_faturamento % 3 == 0:
                    # Somar faturamento e despesas dos três meses
                    faturamento_trimestral = transacoes.filter(
                        data__year=ano_faturamento,
                        data__month__in=[mes_faturamento-2, mes_faturamento-1, mes_faturamento]
                    ).aggregate(total=Sum('transacao'))['total'] or 0

                    despesas_trimestrais = despesas.filter(
                        data__year=ano_faturamento,
                        data__month__in=[mes_faturamento-2, mes_faturamento-1, mes_faturamento]
                    ).aggregate(total=Sum('despesa'))['total'] or 0

                    # Converter para Decimal
                    faturamento_trimestral = Decimal(faturamento_trimestral)
                    despesas_trimestrais = Decimal(despesas_trimestrais)

                    # Calcular o lucro real trimestral
                    lucro_real_trimestral = faturamento_trimestral - despesas_trimestrais

                    if lucro_real_trimestral > 0:
                        valor_imposto = calcular_valor_imposto(lucro_real_trimestral, aliquota, 'trimestral')
                        contexto = {
                            'empresa': empresa.nome,
                            'faturamento': faturamento_trimestral,
                            'despesas': despesas_trimestrais,
                            'lucro_real': lucro_real_trimestral,
                            'imposto': empresa_tributo.nome,
                            'aliquota': empresa_tributo.aliquota,
                            'valor_imposto': valor_imposto,
                            'valor_pagamento': valor_imposto,
                            'vencimento': empresa_tributo.id_data_vencimento_vencimento.dia,
                            'regime': 'trimestral',
                            'trimestre_ano': f"{mes_faturamento-2:02d}-{mes_faturamento:02d}/{ano_faturamento}",
                            'fonte_receita': empresa_tributo.id_fonte_receita_fonte_receita.nome
                        }
                        contextos.append(contexto)

    return contextos


@login_required(login_url='/')
def resultados_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Capturar os valores de mês e ano fornecidos pelo usuário
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    print(mes)
    print(ano)

    # Inicializar os resultados como vazios
    resultados_das = {}
    resultados_lucroPresumido = []
    resultados_lucroReal = []

    # Resultados Simples Nacional
    if empresa.regime_apuracao == "Simples Nacional":
        resultados_das = calcular_das_anual(empresa_id)

    # Resultados Lucro Presumido com filtragem opcional por mês e/ou ano
    if empresa.regime_apuracao == "Lucro Presumido":
        resultados_lucroPresumido = calcular_lucro_presumido_empresa(empresa_id, mes, ano)

    # Resultados Lucro Real com filtragem opcional por mês e/ou ano
    if empresa.regime_apuracao == "Lucro Real":
        resultados_lucroReal = calcular_lucro_real_empresa(empresa_id, mes, ano)

    # Renderizar os resultados com o template
    return render(request, 'frontend/resultados_empresa.html', {
        'empresa': empresa,
        'resultados_das': resultados_das,
        'resultados_lucroPresumido': resultados_lucroPresumido,
        'resultados_lucroReal': resultados_lucroReal,
        'mes': mes,
        'ano': ano,
    })


def calcular_receita_bruta_mes(empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Data atual (ano e mês)
    hoje = date.today()
    ano_atual = hoje.year
    mes_atual = hoje.month

    # Receita bruta do mês atual
    receita_mes = EmpresaTransacoes.objects.filter(
        id_empresa_empresa=empresa,
        id_transacoes_transacoes__data__year=ano_atual,
        id_transacoes_transacoes__data__month=mes_atual
    ).aggregate(total=Sum('id_transacoes_transacoes__transacao'))['total'] or 0

    return {
        'mes_atual': hoje.strftime('%b/%Y'),
        'receita_mes': round(receita_mes, 2),
    }


@login_required(login_url='/')
def adicionarObrigacao(request, empresa_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    if request.method == 'POST':
        obrigacao = request.POST.get("obrigacao")
        data_limite = request.POST.get("data_limite")
        data_envio = request.POST.get("data_envio")

        # Criando um novo critério
        nova_obrigacao = ObrigacaoExtra.objects.create(
            data_limite=data_limite,
            data_envio=data_envio,
            obrigacao = obrigacao
        )

        # Relacionando o critério ao tributo
        EmpresaObrigacao.objects.create(
            id_obrigacao=nova_obrigacao,  # Passando a instância de Criterios
            id_empresa_empresa=empresa  # Passando a instância de Tributo
        )

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/adicionar_obrigacao.html', {'empresa': empresa})

@login_required(login_url='/')
def deletarObrigacao(request, empresa_id, obrigacao_id):
    # Obtendo o tributo pelo id_tributo fornecido
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

    # Obtendo o critério pelo id_aliquotas fornecido
    obrigacao = get_object_or_404(ObrigacaoExtra, id=obrigacao_id)

    # Verificando se o critério está relacionado ao tributo
    empresa_obrigacao = get_object_or_404(EmpresaObrigacao, id_obrigacao=obrigacao,
                                           id_empresa_empresa=empresa)

    if request.method == 'POST':
        # Deletando a relação entre o critério e o tributo
        empresa_obrigacao.delete()

        # Opcional: Deletar o critério completamente se não estiver relacionado a outro tributo
        obrigacao.delete()

        # Redirecionando para a página de visualização de critérios
        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/deletar_obrigacao.html', {
        'empresa': empresa,
        'obrigacao': obrigacao
    })


@login_required(login_url='/')
def editarObrigacao(request, empresa_id, obrigacao_id):
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    obrigacao = get_object_or_404(ObrigacaoExtra, id=obrigacao_id)

    if request.method == 'POST':
        obrigacao_form = request.POST.get("obrigacao")
        data_limite = request.POST.get("data_limite")
        data_envio = request.POST.get("data_envio")

        obrigacao.obrigacao = obrigacao_form
        obrigacao.data_limite = data_limite
        obrigacao.data_envio = data_envio

        obrigacao.save()

        return redirect('exibirempresas', empresa_id=empresa.id_empresa)

    return render(request, 'frontend/editar_obrigacao.html', {'empresa': empresa, 'obrigacao': obrigacao})
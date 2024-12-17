from django.db import models

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200) 
    pub_date = models.DateTimeField("date published")

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Criterios(models.Model):
    id_aliquotas = models.AutoField(primary_key=True)
    deducao_imposto = models.CharField(max_length=100, blank=True, null=True)
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    aliquota = models.DecimalField(max_digits=10, decimal_places=2)

class Municipal(models.Model):
    id = models.AutoField(primary_key=True)
    ccm = models.CharField(max_length=100, blank=True, null=True)
    login_municipal = models.CharField(max_length=100, blank=True, null=True)
    senha_municipal = models.CharField(max_length=100, blank=True, null=True)
    certificado_digital_municipal = models.BooleanField()

class Vencimento(models.Model):
    id_data_vencimento = models.AutoField(primary_key=True)
    dia = models.DateField(blank=True, null=True)
    periodo_pagamento = models.CharField(max_length=100, blank=True, null=True)

class Estadual(models.Model):
    id = models.AutoField(primary_key=True)
    ie = models.CharField(max_length=100, blank=True, null=True)
    login_estadual = models.CharField(max_length=100, blank=True, null=True)
    senha_estadual = models.CharField(max_length=100, blank=True, null=True)
    certificado_digital_estadual = models.BooleanField()

class Federal(models.Model):
    id = models.AutoField(primary_key=True)
    cnpj = models.CharField(max_length=100, blank=True, null=True)
    login_federal = models.CharField(max_length=100, blank=True, null=True)
    senha_federal = models.CharField(max_length=100, blank=True, null=True)
    certificado_digital_federal = models.BooleanField()

class FonteReceita(models.Model):
    id_fonte_receita = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, blank=True, null=True)

class Transacoes(models.Model):
    id_transacoes = models.AutoField(primary_key=True)
    transacao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    fonte_receita = models.CharField(max_length=100, blank=True, null=True)

class Observacoes(models.Model):
    id = models.AutoField(primary_key=True)
    observacao = models.CharField(max_length=100)

class Historico(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.DateField(blank=True, null=True)
    informacao = models.CharField(max_length=100)

class Tributo(models.Model):
    id_tributo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    envio_email = models.DateField(blank=True, null=True)
    confirmacao_email = models.DateField(blank=True, null=True)
    aliquota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    regime = models.CharField(max_length=100, null=True, blank=True)
    id_data_vencimento_vencimento = models.ForeignKey(Vencimento, on_delete=models.CASCADE)
    id_fonte_receita_fonte_receita = models.ForeignKey(FonteReceita, on_delete=models.CASCADE)

class CriterioAliquotas(models.Model):
    id = models.AutoField(primary_key=True)
    id_aliquotas_criterios = models.ForeignKey(Criterios, on_delete=models.CASCADE)
    id_tributo_tributo = models.ForeignKey(Tributo, on_delete=models.CASCADE)

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    responsaveis = models.CharField(max_length=100, blank=True, null=True)
    atividade = models.CharField(max_length=100, blank=True, null=True)
    federal = models.ForeignKey(Federal, on_delete=models.CASCADE)
    estadual = models.ForeignKey(Estadual, on_delete=models.CASCADE)
    municipal = models.ForeignKey(Municipal, on_delete=models.CASCADE)
    regime_apuracao = models.CharField(max_length=100, blank=True, null=True)

class HistoricoEmpresa(models.Model):
    id = models.AutoField(primary_key=True)
    id_historico = models.ForeignKey(Historico, on_delete=models.CASCADE)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

class EmpresaFonteReceita(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_fonte_receita_fonte_receita = models.ForeignKey(FonteReceita, on_delete=models.CASCADE)

class EmpresaTransacoes(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_transacoes_transacoes = models.ForeignKey(Transacoes, on_delete=models.CASCADE)

class EmpresaObservacao(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_observacoes = models.ForeignKey(Observacoes, on_delete=models.CASCADE)

class EmpresaTributo(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_tributo_tributo = models.ForeignKey(Tributo, on_delete=models.CASCADE)

class DepartamentoDP(models.Model):
    id =  models.AutoField(primary_key=True)
    imposto = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_com_juros = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    forma_envio = models.CharField(max_length=100, blank=True, null=True)
    confirmacao = models.CharField(max_length=100, blank=True, null=True)
    data_pagamento = models.DateField(blank=True, null=True)

class Empresa_DP(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_dp_dp = models.ForeignKey(DepartamentoDP, on_delete=models.CASCADE)

class Despesas(models.Model):
    id = models.AutoField(primary_key=True)
    despesa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    motivo = models.CharField(max_length=100, blank=True, null=True)

class EmpresaDespesas(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_despesa_despesa = models.ForeignKey(Despesas, on_delete=models.CASCADE)
    
class SimplesNacional(models.Model):
    id = models.AutoField(primary_key=True)
    numero_anexo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)

class Anexos(models.Model):
    id = models.AutoField(primary_key=True)
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    aliquota = models.DecimalField(max_digits=10, decimal_places=2)
    deducao = models.DecimalField(max_digits=10, decimal_places=2)

class SimplesAnexo(models.Model):
    id = models.AutoField(primary_key=True)
    id_simples = models.ForeignKey(SimplesNacional, on_delete=models.CASCADE)
    id_anexo = models.ForeignKey(Anexos, on_delete=models.CASCADE)

class EmpresaSimples(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_simples = models.ForeignKey(SimplesNacional, on_delete=models.CASCADE)




    

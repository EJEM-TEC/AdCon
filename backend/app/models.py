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
    deducao_imposto = models.IntegerField()
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aliquota = models.DecimalField(max_digits=10, decimal_places=2)

class Municipal(models.Model):
    ccm = models.AutoField(primary_key=True)
    login_municipal = models.CharField(max_length=100, null=True, blank=True)
    senha_municipal = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_municipal = models.BooleanField()

class Vencimento(models.Model):
    id_data_vencimento = models.AutoField(primary_key=True)
    dia = models.DateField(null=True, blank=True)
    periodo_pagamento = models.CharField(max_length=100, null=True, blank=True)


class Estadual(models.Model):
    ie = models.AutoField(primary_key=True)
    login_estadual = models.CharField(max_length=100, null=True, blank=True)
    senha_estadual = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_estadual = models.BooleanField()



class Federal(models.Model):
    cnpj = models.AutoField(primary_key=True)
    login_federal = models.CharField(max_length=100, null=True, blank=True)
    senha_federal = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_federal = models.BooleanField()


class FonteReceita(models.Model):
    id_fonte_receita = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)


class Transacoes(models.Model):
    id_transacoes = models.AutoField(primary_key=True)
    transacao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    fonte_receita = models.CharField(max_length=100, null=True, blank=True)



class Tributo(models.Model):
    id_tributo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    id_data_vencimento_vencimento = models.ForeignKey(Vencimento, on_delete=models.CASCADE)
    id_fonte_receita_fonte_receita = models.ForeignKey(FonteReceita, on_delete=models.CASCADE)



class CriterioAliquotas(models.Model):
    id = models.AutoField(primary_key=True)
    id_aliquotas_criterios = models.ForeignKey(Criterios, on_delete=models.CASCADE)
    id_tributo_tributo = models.ForeignKey(Tributo, on_delete=models.CASCADE)


class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    responsaveis = models.CharField(max_length=100, null=True, blank=True)
    atividade = models.CharField(max_length=100, null=True, blank=True)
    cnpj_federal = models.ForeignKey(Federal, on_delete=models.CASCADE)
    ie_estadual = models.ForeignKey(Estadual, on_delete=models.CASCADE)
    ccm_municipal = models.ForeignKey(Municipal, on_delete=models.CASCADE)
    regime_apuracao = models.CharField(max_length=100, null=True, blank=True)


class EmpresaFonteReceita(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_fonte_receita_fonte_receita = models.ForeignKey(FonteReceita, on_delete=models.CASCADE)

class EmpresaTransacoes(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_transacoes_transacoes = models.ForeignKey(Transacoes, on_delete=models.CASCADE)


class EmpresaTributo(models.Model):
    id = models.AutoField(primary_key=True)
    id_empresa_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_tributo_tributo = models.ForeignKey(Tributo, on_delete=models.CASCADE)


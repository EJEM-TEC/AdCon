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
    deducao_imposto = models.CharField(max_length=10, blank=True, null=True)
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aliquota = models.DecimalField(max_digits=10, decimal_places=2)


class Municipal(models.Model):
    ccm = models.IntegerField(primary_key=True)
    login_municipal = models.CharField(max_length=100, null=True, blank=True)
    senha_municipal = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_municipal = models.BooleanField(default=False)

    def __str__(self):
        return self.login_municipal

class Vencimento(models.Model):
    id_data_vencimento = models.AutoField(primary_key=True)
    dia = models.DateField(null=True, blank=True)
    periodo_pagamento = models.CharField(max_length=100, null=True, blank=True)
    mes = models.DateField(null=True, blank=True)

class Receita(models.Model):
    id_fonte_receita = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)

class Estadual(models.Model):
    ie = models.IntegerField(primary_key=True)
    login_estadual = models.CharField(max_length=100, null=True, blank=True)
    senha_estadual = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_estadual = models.BooleanField(default=False)

    def __str__(self):
        return self.login_estadual

class Federal(models.Model):
    cnpj = models.IntegerField(primary_key=True)
    login_federal = models.CharField(max_length=100, null=True, blank=True)
    senha_federal = models.CharField(max_length=100, null=True, blank=True)
    certificado_digital_federal = models.BooleanField(default=False)

    def __str__(self):
        return self.login_federal

class Tributo(models.Model):
    id_tributo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    id_fonte_receita_receita = models.ForeignKey(Receita, on_delete=models.CASCADE, db_column='id_fonte_receita_receita')
    id_data_vencimento_vencimento = models.ForeignKey(Vencimento, on_delete=models.CASCADE, db_column='id_data_vencimento_vencimento')
    id_aliquotas_Criterios = models.ForeignKey(Criterios, on_delete=models.CASCADE, db_column='id_aliquotas_Criterios')

    def __str__(self):
        return self.nome

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    responsaveis = models.CharField(max_length=100, null=True, blank=True)
    atividade = models.CharField(max_length=100, null=True, blank=True)
    regime_apuracao = models.CharField(max_length=100, null=True, blank=True)
    cnpj_federal = models.ForeignKey(Federal, on_delete=models.CASCADE, db_column='cnpj_federal')
    ie_estadual = models.ForeignKey(Estadual, on_delete=models.CASCADE, db_column='ie_estadual')
    ccm_municipal = models.ForeignKey(Municipal, on_delete=models.CASCADE, db_column='ccm_municipal')
    id_tributo_tributo = models.ForeignKey(Tributo, on_delete=models.CASCADE, db_column='id_tributo_tributo')

    def __str__(self):
        return self.nome

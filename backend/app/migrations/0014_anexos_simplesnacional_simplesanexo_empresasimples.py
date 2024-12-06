# Generated by Django 5.1 on 2024-11-15 21:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_despesas_alter_departamentodp_data_pagamento_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anexos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('limite_superior', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('limite_inferior', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('aliquota', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deducao', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SimplesNacional',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numero_anexo', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SimplesAnexo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id_anexo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.anexos')),
                ('id_simples', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.simplesnacional')),
            ],
        ),
        migrations.CreateModel(
            name='EmpresaSimples',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id_empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.empresa')),
                ('id_simples', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.simplesnacional')),
            ],
        ),
    ]

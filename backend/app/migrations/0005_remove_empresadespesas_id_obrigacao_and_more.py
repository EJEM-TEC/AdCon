# Generated by Django 5.1 on 2025-01-28 21:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_obrigacaoextra_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empresadespesas',
            name='id_obrigacao',
        ),
        migrations.AddField(
            model_name='empresadespesas',
            name='id_despesa_despesa',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.despesas'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='EmpresaObrigacao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id_empresa_empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.empresa')),
                ('id_obrigacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.obrigacaoextra')),
            ],
        ),
    ]

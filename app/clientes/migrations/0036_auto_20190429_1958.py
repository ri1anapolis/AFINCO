# Generated by Django 2.2 on 2019-04-29 19:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0035_clientepagamentos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientepagamentos',
            name='data_pagamento',
            field=models.DateField(blank=True, default=django.utils.timezone.now, help_text='Data do pagamento.', null=True, verbose_name='Data do pagamento'),
        ),
    ]

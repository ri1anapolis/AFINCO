# Generated by Django 2.2 on 2019-04-23 19:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0030_clienteservicos_observacoes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='endereco_complemento',
        ),
        migrations.AddField(
            model_name='cliente',
            name='outorgante',
            field=models.ForeignKey(blank=True, help_text='Pessoa/Entidade que é representada por este cliente (quando aplicável).', limit_choices_to={'ativo': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='clientes.Cliente', verbose_name='Outorgante'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='saldo',
            field=models.FloatField(blank=True, default=0, help_text='Saldo dos créditos da conta do cliente.', null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Saldo'),
        ),
    ]

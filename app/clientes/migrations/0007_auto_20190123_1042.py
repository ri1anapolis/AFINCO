# Generated by Django 2.1.5 on 2019-01-23 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0006_auto_20190123_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienteservicos',
            name='tipo_protocolo',
            field=models.CharField(blank=True, choices=[('CE', 'Certidão'), ('RE', 'Registro'), ('EX', 'Exame e Cálculo')], default='CE', help_text='Tipo do protocolo do register', max_length=2, null=True, verbose_name='Tipo de protocolo'),
        ),
    ]

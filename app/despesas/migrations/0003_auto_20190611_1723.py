# Generated by Django 2.2.1 on 2019-06-11 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0002_auto_20190131_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoriadespesa',
            options={'ordering': ['ativo', 'identificacao', 'codigo_rf'], 'verbose_name': 'Categoria de Despesa', 'verbose_name_plural': 'Categorias de Despesas'},
        ),
        migrations.AlterModelOptions(
            name='despesa',
            options={'ordering': ['-data_despesa', '-id'], 'verbose_name': 'Despesa', 'verbose_name_plural': 'Despesas'},
        ),
        migrations.AddField(
            model_name='categoriadespesa',
            name='conta_credito',
            field=models.PositiveIntegerField(blank=True, help_text='Conta onde será creditado o valor.', null=True, verbose_name='Conta de Crédito'),
        ),
        migrations.AddField(
            model_name='categoriadespesa',
            name='conta_debito',
            field=models.PositiveIntegerField(blank=True, help_text='Conta onde será debitado o valor.', null=True, verbose_name='Conta de Débito'),
        ),
        migrations.AlterField(
            model_name='categoriadespesa',
            name='identificacao',
            field=models.CharField(help_text='Discriminação do tipo de despesa.', max_length=200, verbose_name='Descrição'),
        ),
        migrations.AlterField(
            model_name='despesa',
            name='valor',
            field=models.DecimalField(decimal_places=2, help_text='Valor da despesa.', max_digits=10, verbose_name='Valor'),
        ),
    ]

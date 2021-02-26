from django.contrib import admin

from . import models, forms


class CategoriaDespesaAdmin(admin.ModelAdmin):
    form = forms.CategoriaDespesaForm
    list_display = [
        'identificacao',
        'codigo_rf',
        'conta_credito',
        'conta_debito',
        'ativo',
    ]
    list_filter = [
        'ativo',
    ]
    search_fields = [
        'identificacao',
        'codigo_rf',
    ]


class DespesaAdmin(admin.ModelAdmin):
    form = forms.DespesaForm
    list_display = [
        'display_data_despesa',
        'identificacao',
        'categoria_despesa',
        'display_valor',
    ]
    list_filter = [
        'data_despesa',
        'categoria_despesa',
        'valor',
    ]
    search_fields = [
        'identificacao',
        'categoria_despesa__identificacao',
    ]

    def display_valor(self, obj):
        """Retorna o valor formatado."""
        return f'R$ {obj.valor:.2f}'
    display_valor.short_description = 'Valor'
    display_valor.admin_order_field = 'valor'

    def display_data_despesa(self, obj):
        """Retorna a data formatada."""
        if obj.data_despesa:
            return obj.data_despesa.strftime('%d/%m/%Y')
        return '-'
    display_data_despesa.short_description = 'Data de Pagamento'
    display_data_despesa.admin_order_field = 'data_despesa'


class HistoricosDespesasAdmin(admin.ModelAdmin):
    list_display = [
        'identificacao',
    ]
    search_fields = [
        'identificacao',
    ]

admin.site.register(models.CategoriaDespesa, CategoriaDespesaAdmin)
admin.site.register(models.Despesa, DespesaAdmin)
admin.site.register(models.HistoricosDespesas, HistoricosDespesasAdmin)

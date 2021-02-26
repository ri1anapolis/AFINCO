from django.contrib import admin

from . import models
from caixa.models import LancamentoDeposito
from clientes.models import ClientePagamentos


class LancamentoDepositoInline(admin.TabularInline):
    model = LancamentoDeposito
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ClientePagamentosInline(admin.TabularInline):
    model = ClientePagamentos
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DepositosAdmin(admin.ModelAdmin):
    list_display = [
        'display_data_deposito',
        'identificacao',
        'display_valor',
        'consolidado',
    ]
    list_filter = [
        'data_deposito',
        'consolidado',
        'data_add_reg',
        'data_mod_reg',
    ]
    search_fields = [
        'data_deposito',
        'identificacao',
        'observacoes',
        'valor',
    ]
    readonly_fields = [
        'usuario',
        'data_add_reg',
        'data_mod_reg',
    ]
    inlines = [
        LancamentoDepositoInline,
        ClientePagamentosInline,
    ]

    def display_valor(self, obj):
        """Retorna o valor formatado."""
        return f'R$ {obj.valor:.2f}'
    display_valor.short_description = 'Valor'
    display_valor.admin_order_field = 'valor'

    def display_data_deposito(self, obj):
        """Retorna a data formatada."""
        if obj.data_deposito:
            return obj.data_deposito.strftime('%d/%m/%Y')
        return '-'
    display_data_deposito.short_description = 'Data'
    display_data_deposito.admin_order_field = 'data_deposito'

    class Media:
        js = (
            '/static/js/depositos_admin.js',
        )

    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        try:
            if (
                not obj.lancamentodeposito_set.select_related() or
                not obj.clientepagamentos_set.select_related()
            ):  # editing an existing object
                raise Exception

        except Exception:
            pass

        else:
            return [
                'data_deposito',
                'valor',
                'identificacao',
                'observacoes',
            ] + self.readonly_fields

        return self.readonly_fields


admin.site.register(models.Depositos, DepositosAdmin)

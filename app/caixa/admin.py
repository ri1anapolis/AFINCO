from django.contrib import admin
from django.utils import timezone

from . import models
from clientes.models import ClienteServicos


class ComprovanteInline(admin.TabularInline):
    model = models.Comprovante
    extra = 0


class ChequeInline(admin.TabularInline):
    model = models.Cheque
    extra = 0


class LancamentoDepositoInline(admin.TabularInline):
    model = models.LancamentoDeposito
    extra = 0
    raw_id_fields = ['deposito', ]

    def has_add_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True


class ClienteServicosInline(admin.TabularInline):
    model = ClienteServicos
    extra = 0
    fields = ['cliente', 'data', 'tipo_protocolo', 'protocolo', 'valor', 'liquidado']
    readonly_fields = ['liquidado']

    def has_add_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True


class FechamentoCaixaAdmin(admin.ModelAdmin):
    model = models.FechamentoCaixa
    fieldsets = (
        (None, {
            'fields': (
                'usuario', 'guiche', 'data', 'observacoes',
                ('fechado', 'consolidado', ),
            ),
        }),
        ('Historico', {
            'classes': ('collapse', ),
            'fields': ('historico', 'data_mod_reg', 'usuario_mod', ),
        }),
        ('Saldo Final do Fechamento de Caixa', {
            'fields': (
                'valor_total_entrada', 'valor_quebra',
                'valor_total', 'qtd_devolucoes',
            ),
        }),
        ('Cofre', {
            'fields': ('valor_dinheiro_cofre', 'valor_depositos', 'valor_cheques',
            'valor_comprovantes', 'valor_cartoes')
        }),
        ('Dinheiro em Caixa', {
            'fields': (
                ('saldo_inicial', 'valor_dinheiro_caixa', ),
                ('qtd_moeda_01cent', 'qtd_moeda_05cent'),
                ('qtd_moeda_10cent', 'qtd_moeda_25cent'),
                ('qtd_moeda_50cent', 'qtd_moeda_01real'),
                ('qtd_moeda_02reais', 'qtd_moeda_05reais'),
                ('qtd_moeda_10reais', 'qtd_moeda_20reais'),
                ('qtd_moeda_50reais', 'qtd_moeda_100reais'),
            ),
        }),
        ('Valores Futuros', {
            'fields': (('valor_total_servicos_clientes', 'valor_desp_futuras',), ),
        }),
    )
    readonly_fields = [
        'historico',
        'data_mod_reg',
        'usuario_mod',
    ]
    list_display = [
        'display_data',
        'usuario',
        'guiche',
        'display_valor_quebra',
        'display_valor_total',
        'fechado',
        'consolidado',
    ]
    list_filter = [
        'data',
        'usuario',
        'guiche',
        'fechado',
        'consolidado',
    ]
    inlines = [
        ComprovanteInline,
        ChequeInline,
        LancamentoDepositoInline,
        ClienteServicosInline,
    ]

    def display_valor_quebra(self, obj):
        """Retorna o valor formatado."""
        return f'R$ {obj.valor_quebra:.2f}'
    display_valor_quebra.short_description = 'Quebra de Caixa'
    display_valor_quebra.admin_order_field = 'valor_quebra'

    def display_valor_total(self, obj):
        """Retorna o valor formatado."""
        return f'R$ {obj.valor_total:.2f}'
    display_valor_total.short_description = 'Total'
    display_valor_total.admin_order_field = 'valor_total'

    def display_data(self, obj):
        """Retorna a data formatada."""
        if obj.data:
            return obj.data.strftime('%d/%m/%Y')
        return '-'
    display_data.short_description = 'Data'
    display_data.admin_order_field = 'data'

    def save_model(self, request, obj, form, change):
        historico_txt = '\n{0} {1} salvou alterações via painel administrativo.'.format(
            str(timezone.now()),
            request.user,
        )

        obj.usuario_mod = request.user
        if obj.historico is None:
            obj.historico = ''
        obj.historico = obj.historico + historico_txt
        obj.save()


class ConfiguracaoCaixaAdmin(admin.ModelAdmin):
    model = models.ConfiguracaoCaixa
    filter_horizontal = ['usuarios']


admin.site.register(models.FechamentoCaixa, FechamentoCaixaAdmin)
admin.site.register(models.ConfiguracaoCaixa, ConfiguracaoCaixaAdmin)

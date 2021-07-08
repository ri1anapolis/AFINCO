from django.contrib import admin
from django.db.models import ProtectedError
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from . import forms, models


class ConfiguracoesAdmin(admin.ModelAdmin):
    form = forms.ConfiguracoesForm
    list_display = [
        "display_nome_id",
        "display_valor_custa_register",
        "display_taxa_debito",
        "display_taxa_credito",
    ]

    def display_nome_id(self, obj):
        return f"{obj}"

    display_nome_id.short_description = "Configuração"
    display_nome_id.admin_order_field = "id"

    def display_valor_custa_register(self, obj):
        return f"R$ {obj.valor_custa_register:.2f}" if obj.valor_custa_register else "-"

    display_valor_custa_register.short_description = "Valor da custa"
    display_valor_custa_register.admin_order_field = "valor_custa_register"

    def display_taxa_debito(self, obj):
        """Retorna o valor formatado."""
        return f"{obj.taxa_debito:.2f}%" if obj.taxa_debito else "-"

    display_taxa_debito.short_description = "Taxa a débito"
    display_taxa_debito.admin_order_field = "taxa_debito"

    def display_taxa_credito(self, obj):
        """Retorna o valor formatado."""
        return f"{obj.taxa_credito:.2f}%" if obj.taxa_credito else "-"

    display_taxa_credito.short_description = "Taxa a crédito"
    display_taxa_credito.admin_order_field = "taxa_credito"

    def has_add_permission(self, request):
        if models.Configuracoes.objects.all()[:1]:
            return False
        return True


class BandeirasAdmin(admin.ModelAdmin):
    form = forms.BandeirasForm
    list_display = [
        "nome",
        "usar_debito",
        "display_taxa_debito",
        "usar_credito",
        "display_taxa_credito_avista",
        "display_parcelamento",
        "ativo",
    ]
    list_filter = [
        "usar_debito",
        "usar_credito",
        "parcelar",
        "ativo",
    ]

    def get_conf(self, atributo):
        try:
            _conf = models.Configuracoes.objects.all()[:1]
        except:
            pass
        else:
            if _conf:
                return getattr(_conf[0], atributo, None)
        return None

    def display_taxa_debito(self, obj):
        """Retorna o valor formatado."""
        if obj.usar_debito:
            if obj.taxa_debito is None:
                return f"{self.get_conf('taxa_debito'):.2f}% [P]"
            elif obj.taxa_debito == 0:
                return "ZERO"
            else:
                return f"{obj.taxa_debito:.2f}%"
        else:
            return "-"

    display_taxa_debito.short_description = "Taxa a débito"
    display_taxa_debito.admin_order_field = "taxa_debito"

    def display_taxa_credito_avista(self, obj):
        """Retorna o valor formatado."""
        if obj.usar_credito:
            if obj.taxa_credito_avista is None:
                return f"{self.get_conf('taxa_credito'):.2f}% [P]"
            elif obj.taxa_credito_avista == 0:
                return "ZERO"
            else:
                return f"{obj.taxa_credito_avista:.2f}%"
        else:
            return "-"

    display_taxa_credito_avista.short_description = "Taxa a crédito a vista"
    display_taxa_credito_avista.admin_order_field = "taxa_credito_avista"

    def display_parcelamento(self, obj):
        return f"{obj.parcelamento}x" if obj.usar_credito and obj.parcelar else "-"

    display_parcelamento.short_description = "Parcelamento"
    display_parcelamento.admin_order_field = "parcelamento"


class RegistrosCartoesAdmin(admin.ModelAdmin):
    form = forms.RegistrosCartoesForm
    list_display = [
        "display_data_registro",
        "usuario",
        "bandeira",
        "operacao",
        "display_valor_servico",
        "display_valor_cobrado",
    ]
    list_filter = [
        "data_registro",
        "bandeira",
        "operacao",
        "usuario",
    ]
    search_fields = [
        "protocolo",
        "bandeira__nome",
        "valor_cobrado",
        "valor_servico",
    ]

    def display_data_registro(self, obj):
        return obj.data_registro.strftime("%d/%m/%Y") if obj.data_registro else "-"

    display_data_registro.short_description = "Data do Registro"
    display_data_registro.admin_order_field = "data_registro"

    def display_valor_servico(self, obj):
        return f"R$ {obj.valor_servico:.2f}" if obj.valor_servico else "-"

    display_valor_servico.short_description = "Valor do Serviço"
    display_valor_servico.admin_order_field = "valor_servico"

    def display_valor_cobrado(self, obj):
        return f"R$ {obj.valor_cobrado:.2f}" if obj.valor_cobrado else "-"

    display_valor_cobrado.short_description = "Valor Cobrado"
    display_valor_cobrado.admin_order_field = "valor_cobrado"

    def get_form(self, request, obj=None, **kwargs):
        RCForm = super(RegistrosCartoesAdmin, self).get_form(request, obj, **kwargs)

        class RequestRCForm(RCForm):
            def __new__(cls, *args, **kwargs):
                kwargs["request"] = request
                return RCForm(*args, **kwargs)

        return RequestRCForm

    def delete_view(self, request, object_id, extra_context=None):
        try:
            return super().delete_view(request, object_id, extra_context)
        except ProtectedError:
            msg = (
                "Este registro não pode ser removido pois está "
                "vinculado a um fechamento de caixa consolidado!"
            )
            self.message_user(request, msg, messages.ERROR)
            opts = self.model._meta
            return_url = reverse(
                f"admin:{opts.app_label}_{opts.model_name}_change",
                args=(object_id,),
                current_app=self.admin_site.name,
            )
            return redirect(return_url)

    def response_action(self, request, queryset):
        try:
            return super().response_action(request, queryset)
        except ProtectedError:
            msg = (
                "Um registro não pode ser removido pois está "
                "vinculado a um fechamento de caixa consolidado!"
            )
            self.message_user(request, msg, messages.ERROR)
            opts = self.model._meta
            return_url = reverse(
                f"admin:{opts.app_label}_{opts.model_name}_changelist",
                current_app=self.admin_site.name,
            )
            return redirect(return_url)


admin.site.register(models.Configuracoes, ConfiguracoesAdmin)
admin.site.register(models.Bandeiras, BandeirasAdmin)
admin.site.register(models.RegistrosCartoes, RegistrosCartoesAdmin)

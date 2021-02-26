from django.contrib import admin
from django.utils import timezone
from django.contrib import messages

from . import models
from . import forms


class ClienteInline(admin.TabularInline):
    model = models.Cliente
    extra = 0
    fields = [
        "nome",
        "telefone",
        "endereco",
        "ativo",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ClienteAdmin(admin.ModelAdmin):
    form = forms.ClienteForm
    list_display = [
        "nome",
        "perfil",
        "outorgante",
        "display_saldo",
        "ativo",
    ]
    list_filter = [
        "perfil",
        "ativo",
    ]
    inlines = [
        ClienteInline,
    ]

    def display_saldo(self, obj):
        """Retorna o saldo formatado."""
        return f"R$ {obj.saldo:.2f}"

    display_saldo.short_description = "Saldo"
    display_saldo.admin_order_field = "saldo"

    def get_inline_instances(self, request, obj=None):
        """Retorna o inline de clientes relacionados apenas se o objeto
        não possuir outorgante.
        """
        _inlines = super().get_inline_instances(request, obj=None)
        if getattr(obj, "outorgante", False):
            return []
        return _inlines

    class Media:
        js = ("/static/js/clientes_admin.js",)


class PerfilClienteAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "periodo_pag",
        "ativo",
    ]
    list_filter = [
        "periodo_pag",
        "ativo",
    ]


class ClienteServicosAdmin(admin.ModelAdmin):
    form = forms.ClienteServicosForm
    list_display = [
        "display_data",
        "cliente",
        "tipo_protocolo",
        "protocolo",
        "display_valor",
        "liquidado",
        "contabilizar",
    ]
    list_filter = [
        "data",
        "liquidado",
        "tipo_protocolo",
        "cliente",
        "contabilizar",
    ]
    search_fields = [
        "data",
        "protocolo",
        "cliente",
        "valor",
    ]

    def display_valor(self, obj):
        """Retorna o valor formatado."""
        return f"R$ {obj.valor:.2f}"

    display_valor.short_description = "Valor"
    display_valor.admin_order_field = "valor"

    def display_data(self, obj):
        """Retorna a data formatada."""
        if obj.data:
            return obj.data.strftime("%d/%m/%Y")
        return "-"

    display_data.short_description = "Data"
    display_data.admin_order_field = "data"

    class Media:
        js = ("/static/js/clienteservicos_admin.js",)

    def get_readonly_fields(self, request, obj=None):
        try:
            if obj.caixa and obj.caixa is not None:  # editing an existing object
                return [
                    "cliente",
                    "data",
                    "tipo_protocolo",
                    "protocolo",
                    "contabilizar",
                    "valor",
                ] + self.readonly_fields
        except Exception:
            pass

        return self.readonly_fields


class ClienteFaturasAdmin(admin.ModelAdmin):
    form = forms.ClienteFaturasForm
    create_form = forms.ClienteFaturasCreateForm
    readonly_fields = [
        "data_fatura",
    ]
    list_display = [
        "display_data_fatura",
        "cliente",
        "display_valor_fatura",
        "display_data_pagamento",
        "liquidado",
    ]
    list_filter = [
        "data_fatura",
        "data_pagamento",
        "cliente",
    ]
    search_fields = [
        "cliente",
        "data_fatura",
        "data_pagamento",
        "valor_fatura",
        "observacoes",
    ]

    def display_valor_fatura(self, obj):
        """Retorna o valor formatado."""
        return f"R$ {obj.valor_fatura:.2f}"

    display_valor_fatura.short_description = "Valor da Fatura"
    display_valor_fatura.admin_order_field = "valor_fatura"

    def display_data_fatura(self, obj):
        """Retorna a data formatada."""
        if obj.data_fatura:
            return obj.data_fatura.strftime("%d/%m/%Y")
        return "-"

    display_data_fatura.short_description = "Data da Fatura"
    display_data_fatura.admin_order_field = "data_fatura"

    def display_data_pagamento(self, obj):
        """Retorna a data formatada."""
        if obj.data_pagamento:
            return obj.data_pagamento.strftime("%d/%m/%Y")
        return "-"

    display_data_pagamento.short_description = "Data do Pagamento"
    display_data_pagamento.admin_order_field = "data_pagamento"

    class Media:
        js = ("/static/js/clientefaturas_admin.js",)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.create_form

        return super().get_form(request, obj, **kwargs)


class ClientePagamentosAdmin(admin.ModelAdmin):
    form = forms.ClientePagamentosForm
    list_display = [
        "display_data_pagamento",
        "cliente",
        "forma_pagamento",
        "display_valor",
    ]
    list_filter = [
        "cliente",
        "data_pagamento",
        "data_add",
        "valor",
    ]
    readonly_fields = [
        "data_add",
        "data_mod",
    ]

    def display_valor(self, obj):
        """Retorna o valor formatado."""
        return f"R$ {obj.valor:.2f}"

    display_valor.short_description = "Valor"
    display_valor.admin_order_field = "valor"

    def display_data_pagamento(self, obj):
        """Retorna a data formatada."""
        if obj.data_pagamento:
            return obj.data_pagamento.strftime("%d/%m/%Y")
        return "-"

    display_data_pagamento.short_description = "Data de Pagamento"
    display_data_pagamento.admin_order_field = "data_pagamento"

    def get_form(self, request, obj=None, **kwargs):
        CPForm = super(ClientePagamentosAdmin, self).get_form(request, obj, **kwargs)

        class RequestCPForm(CPForm):
            def __new__(cls, *args, **kwargs):
                kwargs["request"] = request
                return CPForm(*args, **kwargs)

        return RequestCPForm

    def has_delete_permission(self, request, obj=None):
        if (  # se a data da ultima modificação for superior a 30 dias
            obj and abs((obj.data_add - timezone.now().date()).days) > 30
        ) and not getattr(
            request.user, "is_superuser", False
        ):  # e o user não for adm
            return False

        if request.POST and request.POST.get("action") == "delete_selected":
            # if '1' in request.POST.getlist('_selected_action'):
            #    messages.error(request, 'A remoção do pagamento "{obj}" é permitida apenas aos administradores.')
            #    return False
            pagamentos = models.ClientePagamentos.objects.filter(
                id__in=request.POST.getlist("_selected_action")
            )

            objs_protegidos = []
            for pagamento in pagamentos:
                if abs(  # se a data da inclusão for superior a 30 dias
                    (pagamento.data_add - timezone.now().date()).days
                ) > 30 and not getattr(
                    request.user, "is_superuser", False
                ):  # e o user não for adm
                    objs_protegidos.append(f"{pagamento}")

            if objs_protegidos:
                objs_prot = '", "'.join(objs_protegidos)
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        f"Não foi possível executar a ação pois há objetos protegidos em meio "
                        f'à seleção que podem ser removidos apenas por administradores: "{objs_prot}"'
                    ),
                )
                return False

        return True


admin.site.register(models.Cliente, ClienteAdmin)
admin.site.register(models.PerfilCliente, PerfilClienteAdmin)
admin.site.register(models.ClienteServicos, ClienteServicosAdmin)
admin.site.register(models.ClienteFaturas, ClienteFaturasAdmin)
admin.site.register(models.ClientePagamentos, ClientePagamentosAdmin)

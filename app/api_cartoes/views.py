from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import ProtectedError
from django.views.generic import View, TemplateView, DetailView
from django.views.generic.edit import BaseCreateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.utils import timezone
import json

from rolepermissions.mixins import HasRoleMixin
from rolepermissions.checkers import has_role

from .models import Configuracoes, Bandeiras, RegistrosCartoes
from .forms import RegistrosCartoesForm

from caixa.get_fcaixa import get_fcaixa_status


def get_cartoes(request):
    _conf_qs = Configuracoes.objects.all()[:1]
    _bandeiras_obj_list = list(
        Bandeiras.objects.filter(ativo=True).order_by("-usar_debito")
    )
    cartoes = {}

    if _conf_qs:
        _taxa_debito = float(getattr(_conf_qs[0], "taxa_debito", 0))
        _taxa_credito = float(getattr(_conf_qs[0], "taxa_credito", 0))
        _bandeiras = []

        for _bandeira in _bandeiras_obj_list:
            _bandeira_dict = {
                "id": _bandeira.id,
                "nome": _bandeira.nome,
                "usar_debito": _bandeira.usar_debito,
                "usar_credito": _bandeira.usar_credito,
            }
            if _bandeira.usar_debito:
                _bandeira_dict["taxa_debito"] = float(
                    getattr(_bandeira, "taxa_debito", None)
                    if _bandeira.taxa_debito
                    else _taxa_debito
                )

            if _bandeira.usar_credito:
                _bandeira_dict["taxa_credito_avista"] = float(
                    getattr(_bandeira, "taxa_credito_avista")
                    if _bandeira.taxa_credito_avista
                    else _taxa_credito
                )
                _bandeira_dict["parcelar"] = _bandeira.parcelar

                if _bandeira.parcelar:
                    _bandeira_dict["modo_6_6"] = _bandeira.taxa_6meses
                    _bandeira_dict["parcelamento"] = _bandeira.parcelamento
                    _bandeira_dict["taxa_credito_parcelado"] = (
                        float(_bandeira.taxa_credito_parcelado)
                        if _bandeira.taxa_credito_parcelado
                        else None
                    )
                    _bandeira_dict["taxa_credito_parcelado_porparcela"] = (
                        float(_bandeira.taxa_credito_parcelado_porparcela)
                        if _bandeira.taxa_credito_parcelado_porparcela
                        else None
                    )

            _bandeiras.append(_bandeira_dict)

        cartoes = {
            "padrao": {"taxa_debito": _taxa_debito, "taxa_credito": _taxa_credito},
            "bandeiras": _bandeiras,
            "form_errors": request.session.pop("form_errors", None),
            "usuario": {
                "id": request.user.id,
                "username": request.user.username,
                "guiche": {
                    "id": request.user.guiche.id
                    if getattr(request.user, "guiche")
                    else None,
                    "nome": request.user.guiche.nome
                    if getattr(request.user, "guiche")
                    else None,
                },
            },
        }

    return cartoes


def get_registros(usuario_id, data_registro, request_user, force_delete_perms=None):
    fcaixa_status = get_fcaixa_status(usuario_id, data_registro)

    registros = list(
        RegistrosCartoes.objects.filter(
            usuario=usuario_id,
            data_registro=data_registro,
        ).order_by("id")
    )

    registros_json = {
        "registros": [],
        "total_valor_servico": 0,
        "total_valor_cobrado": 0,
    }

    can_delete = False
    if force_delete_perms is None and (
        request_user.id == usuario_id
        or has_role(request_user, ["oficial", "contador"])
        or request_user.is_superuser
    ):
        can_delete = True
    if force_delete_perms is True:
        can_delete = True
    if force_delete_perms is False or fcaixa_status in ["consolidado", "fechado"]:
        can_delete = False

    for registro in registros:
        registros_json["total_valor_servico"] += float(registro.valor_servico)
        registros_json["total_valor_cobrado"] += float(registro.valor_cobrado)

        registros_json["registros"].append(
            {
                "id": registro.id,
                "data_registro": registro.data_registro.strftime("%Y-%m-%d"),
                "usuario": {
                    "id": registro.usuario.id,
                    "username": registro.usuario.username,
                },
                "bandeira": {
                    "id": registro.bandeira.id,
                    "nome": registro.bandeira.nome,
                },
                "operacao": registro.get_operacao_display(),
                "valor_servico": float(registro.valor_servico),
                "valor_cobrado": float(registro.valor_cobrado),
                "taxa_juros": float(registro.taxa_juros),
                "valor_juros": float(registro.valor_cobrado - registro.valor_servico),
                "parcelas": registro.parcelas if registro.parcelas else "-",
                "protocolo": registro.protocolo if registro.protocolo else "-",
                "delete": can_delete,
            }
        )

    return registros_json


def fcaixa_block(request):
    _data_registro = timezone.now()
    if request.POST.get("data_registro"):
        _data_registro = request.POST["data_registro"]

    if _data_registro:
        fcaixa_status = get_fcaixa_status(request.user.id, _data_registro)

        if fcaixa_status in ["consolidado", "fechado"]:
            return fcaixa_status

    return False


class ApiCartoes(LoginRequiredMixin, View):
    def get(self, request):
        resp = get_cartoes(request)
        return JsonResponse(resp, safe=False)


class ApiRegistrosCartoes(LoginRequiredMixin, View):
    def get(self, request):
        resp = json.dumps(get_registros(request.user.id, timezone.now(), request.user))
        return JsonResponse(resp, safe=False)


class Cartoes(LoginRequiredMixin, TemplateView):
    template_name = "cartoes.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        cartoes = get_cartoes(self.request)
        registros = get_registros(
            self.request.user.id, timezone.now(), self.request.user
        )

        context = super().get_context_data(**kwargs)
        context["cartoes"] = cartoes
        context["cartoes_json"] = json.dumps(cartoes)
        context["registros"] = registros
        context["registros_json"] = json.dumps(registros)

        return context


class RegistrosCartoesCreate(LoginRequiredMixin, BaseCreateView):
    form_class = RegistrosCartoesForm
    model = RegistrosCartoes
    login_url = "login"

    def post(self, request, *args, **kwargs):
        fcaixa_status = fcaixa_block(request)
        if fcaixa_status:
            messages.warning(
                request,
                f"Não foi possível adicionar novo registro pois o caixa está {fcaixa_status}!",
            )
            return redirect("cartoes")
        else:
            return super().post(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy("regcartoes_recibo", kwargs={"pk": kwargs["pk"]})
        else:
            return reverse_lazy("regcartoes_recibo", args=(self.object.id,))

    def get_form_kwargs(self):
        kwargs = super(RegistrosCartoesCreate, self).get_form_kwargs()
        kwargs.update(
            {
                "request": self.request,
                "from_my_view": True,
            }
        )
        return kwargs

    def form_invalid(self, form):
        self.request.session["form_errors"] = json.loads(form.errors.as_json())

        return redirect("cartoes")


class RegistrosCartoesRecibo(LoginRequiredMixin, DetailView):
    model = RegistrosCartoes
    template_name = "cartoes_recibo.html"
    context_object_name = "recibo"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context["object"]
        obj.valor_taxa = obj.valor_cobrado - obj.valor_servico

        return context


class RegistrosCartoesDeleteView(LoginRequiredMixin, HasRoleMixin, DeleteView):
    """Remove registro de pagamento com cartão"""

    allowed_roles = [
        "oficial",
        "contador",
        "supervisor_atendimento",
        "atendente",
    ]
    model = RegistrosCartoes
    template_name = "cartoes_registro_delete.html"
    context_object_name = "registro"
    login_url = "login"
    success_url = reverse_lazy("cartoes")

    def post(self, request, *args, **kwargs):
        fcaixa_status = fcaixa_block(request)
        if fcaixa_status:
            messages.warning(
                request,
                f"Não foi possível remover o registro pois o caixa está {fcaixa_status}!",
            )
            return redirect("cartoes")
        else:
            try:
                return self.delete(request, *args, **kwargs)
            except ProtectedError as e:
                self.object = self.get_object()
                messages.error(
                    self.request,
                    f'Não foi possível remover o registro "{self.object}". Erro: "{e}".',
                )
                return redirect("cartoes")

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request, f"O registro de pagamento em cartão foi removido com sucesso!"
        )
        return super(RegistrosCartoesDeleteView, self).delete(request, *args, **kwargs)

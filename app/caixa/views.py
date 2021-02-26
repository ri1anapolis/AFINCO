# pylint: disable=missing-module-docstring,broad-except,pointless-string-statement
import logging
from datetime import date, timedelta
from pytz import timezone as set_timezone
from sentry_sdk import capture_exception
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import View, TemplateView
from django.utils import timezone
from django.http import JsonResponse
from rolepermissions.mixins import HasRoleMixin
from guiches.models import Guiche
from .models import FechamentoCaixa
from .reposicao_caixa import get_conf_caixas
from .get_clientes import search_clientes
from .get_depositos import search_depositos
from .get_fcaixa_related_data import (
    get_cheques,
    get_depositos,
    get_comprovantes,
    get_clientes_servicos,
)
from .get_register_data import (
    get_valor_total_register,
    get_cheques_register,
    get_servicos_clientes_register,
)
from .fcaixa_helper_functions import (
    valid_dict_value,
    float_o,
    textfield_timezone,
    sanitate_post,
)
from .fcaixa_search import list_busca
from .get_fcaixa import get_fcaixa
from .set_fcaixa_add_related_data import SaveRelatedDataFcaixa
from .set_fcaixa_rem_related_data import RemoveRelatedDataFcaixa
from .set_fcaixa import consolida_depositos

logger = logging.getLogger("afinco")


class FechamentoCaixaView(LoginRequiredMixin, HasRoleMixin, TemplateView):
    """docstring for FechamentoCaixaView"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]
    template_name = "fechamento_caixa.html"


class GetDepositos(LoginRequiredMixin, HasRoleMixin, View):
    """Trata das solicitações por depósitos"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]

    def get(self, request):
        """Responde chamadas GET com lista de depósitos condizentes com o termo informado."""
        term = self.request.GET["term"] if self.request.GET["term"] is not None else ""
        depositos = search_depositos(term)
        return JsonResponse(depositos, safe=False)


class GetClientes(LoginRequiredMixin, HasRoleMixin, View):
    """Busca por clientes cadastrados mediante termo para pesquisa."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]

    def get(self, request):
        """Busca por clientes cadastrados mediante termo para pesquisa."""
        term = self.request.GET["term"] if self.request.GET["term"] is not None else ""
        clientes = search_clientes(term)
        return JsonResponse(clientes, safe=False)


class GetFechamentoCaixa(LoginRequiredMixin, HasRoleMixin, View):
    """Buscas e apresentação de fechamentos de caixas"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]

    def get(self, request):  # pylint: disable=too-many-locals
        """Trata as requisições GET para apresentação das informações de fechamento de caixa"""
        obj_usuario = self.request.user
        fcaixa, status_busca, erro = get_fcaixa(request)
        is_first_fcaixa_ever = bool(fcaixa is None and status_busca == 0)
        fcaixa_values = {**list_busca(obj_usuario)}

        if fcaixa is None and status_busca == 1:
            fcaixa_values.update({"erro": "Nenhum fechamento de caixa encontrado."})
            return JsonResponse(fcaixa_values)
        if status_busca == 2:
            fcaixa_values.update({"erro": erro})
            return JsonResponse(fcaixa_values)

        client_tz = (
            set_timezone(self.request.GET["client_tz"])
            if valid_dict_value(self.request.GET, "client_tz")
            else timezone.get_current_timezone()
        )

        if is_first_fcaixa_ever:
            fcaixa_values.update(
                {
                    "usuario_login": obj_usuario.username,
                    "usuario_id": obj_usuario.id,
                    "guiche_nome": obj_usuario.guiche.nome,
                    "guiche_id": obj_usuario.guiche.id,
                    "data": date.today(),
                },
            )

        else:
            if bool(
                (status_busca == 0 and fcaixa.data < date.today())
                and (fcaixa.fechado or fcaixa.consolidado)
            ):
                """
                Caixa do dia ainda não salvo
                o valor de saldo inicial deve ser o valor em caixa do dia anterior
                """
                fcaixa_values.update(
                    {
                        "saldo_inicial": float_o(fcaixa.valor_dinheiro_caixa),
                        "data": date.today(),
                    }
                )

            else:
                """
                valores que podem ser exibidos tanto em uma busca quanto no caixa
                já salvo do dia
                """
                fcaixa_values.update(
                    {
                        "id": fcaixa.id,
                        "data": fcaixa.data,
                        "fechado": fcaixa.fechado,
                        "consolidado": fcaixa.consolidado,
                        "saldo_inicial": float_o(fcaixa.saldo_inicial),
                        "valor_dinheiro_cofre": float_o(fcaixa.valor_dinheiro_cofre),
                        "valor_depositos": float_o(fcaixa.valor_depositos),
                        "valor_cheques": float_o(fcaixa.valor_cheques),
                        "valor_comprovantes": float_o(fcaixa.valor_comprovantes),
                        "valor_cartoes": float_o(fcaixa.valor_cartoes),
                        "valor_total_servicos_clientes": float_o(
                            fcaixa.valor_total_servicos_clientes
                        ),
                        "valor_desp_futuras": float_o(fcaixa.valor_desp_futuras),
                        "valor_total_entrada": float_o(fcaixa.valor_total_entrada),
                        "valor_quebra": float_o(fcaixa.valor_quebra),
                        "valor_total": float_o(fcaixa.valor_total),
                        "qtd_devolucoes": fcaixa.qtd_devolucoes,
                        "observacoes": fcaixa.observacoes,
                        "depositos": get_depositos(fcaixa.id),
                        "comprovantes": get_comprovantes(fcaixa.id),
                        "cheques": get_cheques(fcaixa.id),
                        "clientes_servicos": get_clientes_servicos(fcaixa.id),
                        "historico": textfield_timezone(fcaixa.historico, client_tz),
                        "usuario_mod": fcaixa.usuario_mod.username
                        if getattr(fcaixa, "usuario_mod")
                        else obj_usuario.username,
                        "data_mod_reg": date.strftime(
                            fcaixa.data_mod_reg.astimezone(tz=client_tz),
                            "%d/%m/%Y às %H:%M:%S",
                        ),
                    }
                )

            """
            informações necessárias que são comuns a qualquer fechamento de caixa 
            que não seja o primeiro
            """
            fcaixa_values.update(
                {
                    "usuario_login": fcaixa.usuario.username,
                    "usuario_id": fcaixa.usuario.id,
                    "guiche_nome": fcaixa.guiche.nome,
                    "guiche_id": fcaixa.guiche.id,
                    "valor_dinheiro_caixa": float_o(fcaixa.valor_dinheiro_caixa),
                    "qtd_moeda_01cent": fcaixa.qtd_moeda_01cent,
                    "qtd_moeda_05cent": fcaixa.qtd_moeda_05cent,
                    "qtd_moeda_10cent": fcaixa.qtd_moeda_10cent,
                    "qtd_moeda_25cent": fcaixa.qtd_moeda_25cent,
                    "qtd_moeda_50cent": fcaixa.qtd_moeda_50cent,
                    "qtd_moeda_01real": fcaixa.qtd_moeda_01real,
                    "qtd_moeda_02reais": fcaixa.qtd_moeda_02reais,
                    "qtd_moeda_05reais": fcaixa.qtd_moeda_05reais,
                    "qtd_moeda_10reais": fcaixa.qtd_moeda_10reais,
                    "qtd_moeda_20reais": fcaixa.qtd_moeda_20reais,
                    "qtd_moeda_50reais": fcaixa.qtd_moeda_50reais,
                    "qtd_moeda_100reais": fcaixa.qtd_moeda_100reais,
                }
            )

        """
        informações para qualquer caixa
        """
        is_consolidado = fcaixa_values.get("consolidado", False)

        # importing here because django doesn't allow to make imports
        # from both files in both files in global scope.
        # pylint: disable=import-outside-toplevel
        from api_cartoes.views import get_registros

        registros_cartoes = get_registros(
            fcaixa_values["usuario_id"],
            fcaixa_values["data"],
            obj_usuario,
            False
            if fcaixa_values["usuario_id"] != obj_usuario.id or is_consolidado
            else None,
        )

        fcaixa_values.update(
            {
                "status_busca": bool(status_busca == 1),
                "registros_cartoes": registros_cartoes,
                "valor_cartoes": registros_cartoes["total_valor_servico"],
            }
        )

        if not is_consolidado and fcaixa_values["data"] > date.today() - timedelta(15):
            """
            informações para qualquer caixa recente (últimos 15 dias) que não estejam
            consolidados. Informações externas: Register e Cartões.
            """

            guiche_register = (
                obj_usuario.guiche.id_register
                if is_first_fcaixa_ever
                else fcaixa.guiche.id_register
            )
            valor_total_register = get_valor_total_register(
                fcaixa_values["data"],
                guiche_register,
            )
            cheques = fcaixa_values.get("cheques", [])
            clientes_servicos = fcaixa_values.get("clientes_servicos", [])

            fcaixa_values.update(
                {
                    "valor_total_register": valor_total_register,
                    "cheques": cheques
                    + get_cheques_register(
                        fcaixa_values["data"],
                        guiche_register,
                        cheques,
                    ),
                    "clientes_servicos": clientes_servicos
                    + get_servicos_clientes_register(
                        guiche_register,
                        fcaixa_values["data"],
                        clientes_servicos,
                    ),
                }
            )

        return JsonResponse(fcaixa_values)


class SetFechamentoCaixa(LoginRequiredMixin, HasRoleMixin, View):
    """Recebe e salva os fechamentos de caixa"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]

    def post(self, request):  # pylint: disable=missing-function-docstring
        post_data = sanitate_post(self.request.body)

        if not bool(
            valid_dict_value(post_data, "id")
            or (
                valid_dict_value(post_data, "guiche_id")
                and valid_dict_value(post_data, "usuario_id")
            )
        ):
            return JsonResponse(
                {"erro": "Informações insuficientes.", "success": False}
            )

        try:
            if valid_dict_value(post_data, "id"):
                f_caixa = FechamentoCaixa.objects.get(id=post_data["id"])

            else:
                f_caixa = FechamentoCaixa.objects.create(
                    guiche=Guiche.objects.get(id=post_data["guiche_id"]),
                    usuario=get_user_model().objects.get(id=post_data["usuario_id"]),
                    data=date.today(),
                    historico=(
                        f"\n{timezone.now()} {self.request.user.username}"
                        " gerou novo fechamento de caixa."
                    ),
                )
                f_caixa.save()

        except Exception as error:
            capture_exception(error)
            return JsonResponse(
                {
                    "erro": (
                        "[A001] Erro ao recuperar informações "
                        f"do fechamento de caixa.\n\t{error}"
                    ),
                    "success": False,
                }
            )

        else:
            save_related = SaveRelatedDataFcaixa()
            remove_related = RemoveRelatedDataFcaixa()
            f_caixa_retorno, erro = {}, ""
            client_tz = (
                set_timezone(post_data["client_tz"])
                if valid_dict_value(post_data, "client_tz")
                else timezone.get_current_timezone()
            )

            for objeto in ("depositos", "cheques", "comprovantes", "clientes_servicos"):
                if valid_dict_value(post_data, f"{objeto}_rem"):
                    erro = getattr(remove_related, f"remove_{objeto}")(
                        post_data[f"{objeto}_rem"],
                        f_caixa.id,
                    )
                if valid_dict_value(post_data, objeto):
                    ids_to_client, erro = getattr(save_related, f"save_{objeto}")(
                        post_data[objeto],
                        f_caixa.id,
                    )
                    f_caixa_retorno.update({f"{objeto}": ids_to_client})

                if erro:
                    return JsonResponse({"erro": erro, "success": False})

            f_caixa, erro = save_related.save_valores(post_data, f_caixa)
            if erro:
                return JsonResponse({"erro": erro, "success": False})

            if bool(post_data.get("consolidado") and not f_caixa.consolidado):
                f_caixa.consolidado = True
                f_caixa.fechado = True
                f_caixa.historico += (
                    f"\n{timezone.now()} {self.request.user.username}"
                    " consolidou o fechamento de caixa."
                )
                f_caixa.save()
                consolida_depositos(f_caixa.id, self.request.user, request)

            elif valid_dict_value(post_data, "fechado"):
                if post_data["fechado"] and not f_caixa.fechado:
                    f_caixa.historico += (
                        f"\n{timezone.now()} {self.request.user.username}"
                        " fechou o caixa, disponibilizando-o para consolidação."
                    )
                elif not post_data["fechado"] and f_caixa.fechado:
                    f_caixa.historico += (
                        f"\n{timezone.now()} {self.request.user.username}"
                        " reabriu o caixa para edição."
                    )
                else:
                    f_caixa.historico += (
                        f"\n{timezone.now()} {self.request.user.username}"
                        " salvou alterações no fechamento de caixa."
                    )

                f_caixa.fechado = post_data["fechado"]

            f_caixa.usuario_mod = self.request.user
            f_caixa.save()

            f_caixa_retorno.update(
                {
                    "id": f_caixa.id,
                    "fechado": f_caixa.fechado,
                    "consolidado": f_caixa.consolidado,
                    "historico": textfield_timezone(f_caixa.historico, client_tz),
                    "usuario_mod": f_caixa.usuario_mod.username,
                    "data_mod_reg": date.strftime(
                        f_caixa.data_mod_reg.astimezone(tz=client_tz),
                        "%d/%m/%Y às %H:%M:%S",
                    ),
                    "erro": "",
                    "success": True,
                }
            )
            return JsonResponse(f_caixa_retorno)


class ReposicaoCaixaView(
    LoginRequiredMixin, HasRoleMixin, TemplateView
):  # pylint: disable=too-many-ancestors
    """View para calculos de reposição de caixa"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento", "atendente"]
    template_name = "reposicao_caixa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["f_caixas"] = get_conf_caixas()
        return context

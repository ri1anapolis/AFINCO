# pylint: disable=missing-module-docstring
from datetime import date
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import intcomma
from depositos.models import Depositos
from depositos.helper_functions import valores


def search_depositos(term):
    """Busca por depósitos dado um termo e retorna um array de com principais informações"""
    depositos = []

    if len(term) > 2:
        obj_depositos = (
            Depositos.objects.filter(
                Q(data_deposito__icontains=term)
                | Q(valor__icontains=str(term).replace(",", "."))
                | Q(identificacao__icontains=term)
                | Q(observacoes__icontains=term)
            )
            .exclude(
                consolidado=True,
            )
            .order_by("identificacao")[:100]
        )

        for deposito in obj_depositos:
            valor_disponivel = valores(deposito)["valor_disponivel"]

            if valor_disponivel > 0:

                valor_disponivel_label = (
                    f"R$ {intcomma(valor_disponivel)} / "
                    if valor_disponivel < float(deposito.valor)
                    else ""
                )
                label = (
                    f"{date.strftime(deposito.data_deposito, '%d/%m/%Y')} :: "
                    f"{valor_disponivel_label}R$ {intcomma(deposito.valor)} :: "
                    f"{deposito.identificacao}"
                )
                value = f"R$ {intcomma(deposito.valor)} - {deposito.identificacao}"

                depositos.append(
                    {
                        "label": label,
                        "value": value,
                        "id": deposito.id,
                        "data_deposito": deposito.data_deposito,
                        "valor_deposito": valor_disponivel,
                        "identificacao": deposito.identificacao,
                        "observacoes": deposito.observacoes,
                        "consolidado": deposito.consolidado,
                    }
                )

    return depositos

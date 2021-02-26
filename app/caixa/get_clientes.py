# pylint: disable=missing-module-docstring
from django.db.models import Q
from clientes.models import Cliente


def search_clientes(term):
    """Busca por clientes dado um termo e retorna um array de com principais informações"""
    clientes = []

    if len(term) > 2:
        obj_clientes = (
            Cliente.objects.filter(
                Q(nome__icontains=term)
                | Q(cpf__icontains=term)
                | Q(cnpj__icontains=term)
                | Q(estrangeiro__icontains=term)
                | Q(telefone__icontains=term)
                | Q(email__icontains=term)
            )
            .exclude(
                Q(ativo=False)
                | ~Q(outorgante=None)
                | (Q(verifica_saldo=True) & Q(saldo__lt=5))
            )
            .order_by("nome")[:12]
        )

        for cliente in obj_clientes:
            documento = ""

            if cliente.tipo_documento == "PF":
                documento = f" (CPF: {cliente.cpf})"
            if cliente.tipo_documento == "PJ":
                documento = f" (CNPJ: {cliente.cnpj})"
            if cliente.tipo_documento == "EX":
                documento = f" (Doc. Estrangeiro: {cliente.estrangeiro})"

            clientes.append(
                {
                    "label": cliente.nome + documento,
                    "value": cliente.nome,
                    "id": cliente.id,
                    "verifica_saldo": cliente.verifica_saldo,
                    "saldo": float(cliente.saldo),
                }
            )
    return clientes

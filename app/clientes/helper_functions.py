# pylint: disable=missing-module-docstring,broad-except
from .models import Cliente


def get_cliente_object(cliente):
    """Retorno o cliente dado um objeto ou id"""
    try:
        if isinstance(cliente, Cliente):
            cliente.refresh_from_db()
            return cliente

        return Cliente.objects.filter(id=cliente).first()

    except Exception:
        return None


def get_cliente_faturas(cliente, valor_fatura=None, liquidadas=None):
    """Retorna as faturas relacionadas ao cliente"""
    cliente = get_cliente_object(cliente)
    faturas_list = []

    try:
        valor_fatura = float(valor_fatura)
    except Exception:
        valor_fatura = None

    if cliente is not None:
        faturas = cliente.clientefaturas_set.select_related().order_by(
            "-data_fatura",
            "-id",
            "-valor_fatura",
        )
        faturas = (
            faturas
            if valor_fatura is None or valor_fatura <= 0
            else faturas.filter(valor_fatura__lte=valor_fatura)
        )
        faturas = (
            faturas if liquidadas is None else faturas.filter(liquidado=liquidadas)
        )

        for fatura in faturas:
            faturas_list.append(
                {
                    "id": fatura.id,
                    "valor_fatura": fatura.valor_fatura,
                    "data_fatura": fatura.data_fatura,
                }
            )

    return faturas_list

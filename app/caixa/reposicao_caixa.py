# pylint: disable=missing-module-docstring
from .models import FechamentoCaixa, ConfiguracaoCaixa


def nto(value=None):
    """None to 0"""
    return 0 if value is None else int(value)


def get_f_caixas():
    """Retorna o último fechamentos de caixa de cada usuário."""
    last_fcaixas = FechamentoCaixa.objects.all().order_by("-data")[:50]

    f_caixa_objs = {}
    for f_caixa in last_fcaixas:
        if f_caixa.usuario.id not in f_caixa_objs.keys():
            f_caixa_objs[f_caixa.usuario.id] = f_caixa

    return f_caixa_objs.values()


def get_conf_caixas():
    """Retorna o os valores para reposição de caixa."""
    total = {"usuario": "Total"}
    extrato_fcaixas = []
    extrato_campos = (
        "qtd_moeda_01cent",
        "qtd_moeda_05cent",
        "qtd_moeda_10cent",
        "qtd_moeda_25cent",
        "qtd_moeda_50cent",
        "qtd_moeda_01real",
        "qtd_moeda_02reais",
        "qtd_moeda_05reais",
        "qtd_moeda_10reais",
        "qtd_moeda_20reais",
        "qtd_moeda_50reais",
        "qtd_moeda_100reais",
    )

    for f_caixa in get_f_caixas():
        fcaixa_extrato = {"usuario": f_caixa.usuario.username}
        try:

            conf = (
                ConfiguracaoCaixa.objects.filter(usuarios=f_caixa.usuario.id)
                .order_by("precedencia")
                .exclude(is_active=False)[:1]
            )

            if conf.count() < 1:
                raise Exception

        except Exception:  # pylint: disable=broad-except
            for campo in extrato_campos:
                fcaixa_extrato[campo] = "N/A"
            extrato_fcaixas.append(fcaixa_extrato)
        else:
            for campo in extrato_campos:
                fcaixa_extrato[campo] = nto(getattr(conf[0], campo)) - nto(
                    getattr(f_caixa, campo)
                )

            extrato_fcaixas.append(fcaixa_extrato)

            for campo in extrato_campos:
                if campo in total:
                    total[campo] += extrato_fcaixas[-1][campo]
                else:
                    total[campo] = extrato_fcaixas[-1][campo]

    extrato_fcaixas = sorted(extrato_fcaixas, key=lambda usuario: usuario["usuario"])

    for campo in extrato_campos:
        if not campo in total:
            total[campo] = "N/A"

    extrato_fcaixas.append(total)

    return extrato_fcaixas

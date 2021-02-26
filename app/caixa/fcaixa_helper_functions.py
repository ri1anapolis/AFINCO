# pylint: disable=missing-module-docstring,broad-except
import logging
import json
import urllib.parse
from datetime import datetime

logger = logging.getLogger("afinco")


def valid_dict_value(_dict_, item):
    """Testa se o dicionário possui valor válido"""

    if _dict_.get(item) is not None:
        if isinstance(_dict_[item], (int, float, bool)):
            return True
        if len(_dict_[item]) > 0:
            return True
    return False


def float_o(value):
    """Tenta converter valor para float ou retorna 0"""
    try:
        return float(value)
    except Exception:
        return 0


def textfield_timezone(text, client_tz):
    """
    Aplica conversão de timezone a todos os data-tempo do texto
    e retorna o texto.
    Por enquanto aplicável apenas para o padrão do campo histórico.
    É esperada data no formato timezone.now().
    É retirado o ponto da parte do offset do timezone devido ao
    strptime não ter uma variável retratando o offset com o ponto.
    """
    try:
        tz_text = ""
        for line in text.splitlines():
            if len(line) > 0:
                text_date = datetime.strftime(
                    datetime.strptime(
                        f"{line[:29]}{line[30:32]}", "%Y-%m-%d %H:%M:%S.%f%z"
                    ).astimezone(client_tz),
                    "%d/%m/%Y %H:%M:%S",
                )
                tz_text += f"\n[ {text_date} ] {line[33:]}"
    except Exception:
        tz_text = None

    return tz_text


def sanitate_post(post_raw_data):
    """
    Recebe os dados do cliente e os prepara para uso:
    Converte do formato url para string (json) e depois converte para dicionário json.
    """
    json_raw_post = json.loads(
        json.dumps(urllib.parse.parse_qs(post_raw_data.decode("utf-8")))
    )
    fcaixa_dict = json.loads(json_raw_post["f_caixa"][0])

    logger.debug("::: SALVAR FCAIXA|Requisição POST:\n\t%s", json_raw_post)

    return fcaixa_dict

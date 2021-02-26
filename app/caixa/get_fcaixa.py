# pylint: disable=missing-module-docstring
import logging
from .models import FechamentoCaixa
from .fcaixa_helper_functions import valid_dict_value
from .fcaixa_search import can_user_search
from .get_fcaixa_related_data import search_fcaixa

logger = logging.getLogger("afinco")


def get_fcaixa(request):
    """
    Dado o objeto de requisição (request) retorna o fechamento de caixa,
    status e mensagem de erro.
    """
    req_user = request.user
    _get = request.GET

    fcaixa_id = _get["fcaixa_id"] if valid_dict_value(_get, "fcaixa_id") else None
    data = _get["data"] if valid_dict_value(_get, "data") else None
    usuario_id = _get["usuario_id"] if valid_dict_value(_get, "usuario_id") else None
    guiche_id = _get["guiche_id"] if valid_dict_value(_get, "guiche_id") else None

    if fcaixa_id or (data and (usuario_id or guiche_id)):
        fcaixa = search_fcaixa(
            fcaixa_id=fcaixa_id,
            data=data,
            usuario_id=usuario_id,
            guiche_id=guiche_id,
        )

        if fcaixa is not None:
            status_busca, erro = can_user_search(req_user, fcaixa.usuario_id)
        else:
            status_busca, erro = 1, ""

    else:
        if req_user.guiche:
            fcaixa = search_fcaixa(
                usuario_id=req_user.id,
                guiche_id=req_user.guiche,
            )
            status_busca, erro = 0, ""
        else:
            fcaixa = None
            status_busca, erro = can_user_search(req_user, None)
            if status_busca > 1:
                erro += " Não há guichê configurado para o usuário!"

    logger.debug("::: BUSCAR FCAIXA|BUSCA CAIXA|Request:\n\t%s\n\t%s", request, _get)
    logger.info("::: BUSCAR FCAIXA|BUSCA CAIXA|Fechamento de caixa:\n\t%s", fcaixa)
    logger.info("::: BUSCAR FCAIXA|BUSCA CAIXA|Status de busca: %s", status_busca)
    logger.info("::: BUSCAR FCAIXA|BUSCA CAIXA|Mensagem de erro: %s", erro)

    return fcaixa, status_busca, erro


def get_fcaixa_status(usuario_id, data_fcaixa):
    """Retorna o status do fechamento de caixa: aberto, fechado ou consolidado"""
    if usuario_id and data_fcaixa:
        fcaixa = (
            FechamentoCaixa.objects.filter(usuario=usuario_id, data=data_fcaixa)
            .order_by("-data")
            .first()
        )

        if not fcaixa:
            return None
        if getattr(fcaixa, "consolidado"):
            return "consolidado"
        if getattr(fcaixa, "fechado"):
            return "fechado"
        return "aberto"

    return None

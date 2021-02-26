# pylint: disable=missing-module-docstring,broad-except
from rolepermissions.checkers import has_role
from sentry_sdk import capture_exception
from .models import FechamentoCaixa


def can_user_search(obj_usuario, obj_f_caixa_usuario_id=None):
    """Retorna o valor 1 caso o usuário indicado possa realizar buscas ou 2 caso não."""
    if (
        has_role(obj_usuario, ["oficial", "contador", "supervisor_atendimento"])
        or obj_usuario.id == obj_f_caixa_usuario_id
    ):
        status_busca, erro = 1, ""
    else:
        status_busca = 2
        erro = f"O usuário {obj_usuario.username} não tem permissões para realizar essa busca."

    return (status_busca, erro)


def list_busca(obj_usuario):
    """Retorna lista de usuários e guichês disponíveis para busca do fechamento de caixa."""
    list_usuarios_busca, list_guiches_busca = [], []

    if has_role(obj_usuario, ["oficial", "contador", "supervisor_atendimento"]):
        try:
            guiches_usuarios = (
                FechamentoCaixa.objects.all()
                .order_by("-data")[:500]
                .values_list(
                    "guiche_id", "guiche__nome", "usuario__id", "usuario__username"
                )
            )
        except Exception as error:
            capture_exception(error)
        else:
            usuarios_guiches_set = list(set(list(guiches_usuarios)))
            guiches, usuarios = [], []
            for item in usuarios_guiches_set:
                guiches.append((item[0], item[1]))
                usuarios.append((item[2], item[3]))

            for guiche in sorted(list(set(guiches)), key=lambda guiche: guiche[1]):
                list_guiches_busca.append({"id": guiche[0], "nome": guiche[1]})

            for usuario in sorted(list(set(usuarios)), key=lambda usuario: usuario[1]):
                list_usuarios_busca.append({"id": usuario[0], "username": usuario[1]})

    elif obj_usuario.guiche:
        try:
            guiches = (
                FechamentoCaixa.objects.filter(usuario_id=obj_usuario.id)
                .order_by("-data")[:100]
                .values_list("guiche_id", "guiche__nome")
            )
        except Exception as error:
            capture_exception(error)
        else:
            guiches_set = list(set(list(guiches)))
            list_usuarios_busca.append(
                {"id": obj_usuario.id, "username": obj_usuario.username}
            )

            for guiche in guiches_set:
                list_guiches_busca.append({"id": guiche[0], "nome": guiche[1]})

    return {
        "list_guiches_busca": list_guiches_busca,
        "list_usuarios_busca": list_usuarios_busca,
    }

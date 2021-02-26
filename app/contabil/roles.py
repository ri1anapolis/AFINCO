from rolepermissions.roles import AbstractUserRole


class Oficial(AbstractUserRole):
    available_permissions = {
        'acesso_total': True,
    }


class Contador(AbstractUserRole):
    available_permissions = {
        'gerar_relatorio_contabil': True,
    }


class Atendente(AbstractUserRole):
    available_permissions = {
        'fechar_caixa': True,
    }

class SupervisorAtendimento(AbstractUserRole):
    available_permissions = {
        'consultar_caixas': True,
    }

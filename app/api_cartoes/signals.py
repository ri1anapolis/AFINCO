from django.db.models import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import RegistrosCartoes
from caixa.get_fcaixa import get_fcaixa_status


@receiver(pre_delete, sender=RegistrosCartoes)
def registros_cartoes_pre_delete(sender, instance, **kwargs):
    fcaixa_status = get_fcaixa_status(instance.usuario.id, instance.data_registro)
    fcaixa_consolidado = True if fcaixa_status == "consolidado" else False

    if fcaixa_consolidado:
        raise ProtectedError(
            "O registro de pagamento em cartão não pode ser removido pois está "
            "vinculado a um fechamento de caixa consolidado!",
            instance,
        )

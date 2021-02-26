from django.db import models
from django.contrib.auth.models import AbstractUser, Group, UserManager, GroupManager


class ProjectUserManager(UserManager):
    pass


class ProjectGroupManager(GroupManager):
    pass


class ProjectUser(AbstractUser):
    guiche = models.ForeignKey(
        'guiches.Guiche',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Guichê',
        help_text='Guichê do usuário.',
    )
    objects = ProjectUserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class ProjectGroup(Group):
    objects = ProjectGroupManager()

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'

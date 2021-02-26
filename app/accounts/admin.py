from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin, Group

from .forms import ProjectUserCreationForm, ProjectUserChangeForm
from .models import ProjectUser, ProjectGroup

from rolepermissions.admin import RolePermissionsUserAdminMixin


class ProjectUserAdmin(RolePermissionsUserAdminMixin, UserAdmin):
    model = ProjectUser
    form = ProjectUserChangeForm
    add_form = ProjectUserCreationForm

    fieldsets = UserAdmin.fieldsets + (
        ('CONTABIL', {
            'fields': (
                'guiche',
            )
        }),
    )


class ProjectGroupAdmin(GroupAdmin):
    model = ProjectGroup


admin.site.register(ProjectUser, ProjectUserAdmin)
admin.site.unregister(Group)
admin.site.register(ProjectGroup, ProjectGroupAdmin)

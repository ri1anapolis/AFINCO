from django.contrib import admin
from . import models


class GuicheAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id_register', 'is_active', ]
    list_filter = ['is_active']


admin.site.register(models.Guiche, GuicheAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from eagle_eyes.apps.eagleusers.models import EagleUser, Config


@admin.register(EagleUser)
class EagleUserAdmin(UserAdmin):
    pass


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('title', )

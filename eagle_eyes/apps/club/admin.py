from django.contrib import admin
import nested_admin

from eagle_eyes.apps.club.models import Mission, Config, Booster, Level


class BoosterInline(nested_admin.NestedTabularInline):
    model = Booster
    extra = 0


@admin.register(Mission)
class MissionAdmin(nested_admin.NestedModelAdmin):
    inlines = [BoosterInline]
    list_display = (
        'title',
        'action',
        'XP',
        'points',
        'is_active'
    )


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = (
        'title',
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'start_xp'
    )

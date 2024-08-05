from django.contrib import admin
from eagle_eyes.apps.lucky_wheel.models import LuckyWheel


@admin.register(LuckyWheel)
class LuckyWheelAdmin(admin.ModelAdmin):
    list_display = ['title', 'campaign', 'chance', 'active']
    ordering = ('campaign',)

    def save_model(self, request, obj, form, change):
        ''' checks if the behsa offer id of a Lucky Wheel has changed. if it has changed, it soft-deletes
            the old Lucky Wheel'''

        if not change:
            return super().save_model(request, obj, form, change)
        old_obj = LuckyWheel.objects.all_with_deleted().filter(id=obj.id).first()
        old_obj.delete()
        obj.id = None
        obj.pk = None
        obj.save()

    def has_change_permission(self, request, obj=None) -> bool:
        if obj is not None and obj.deleted:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None) -> bool:
        if obj is not None and obj.deleted:
            return False
        return super().has_delete_permission(request, obj)

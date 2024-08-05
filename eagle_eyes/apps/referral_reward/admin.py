from django.contrib import admin
from eagle_eyes.apps.referral_reward.models import Reward
import nested_admin


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = [
                    'title',
                    'description',
                    'checkpoint',
                    'offer_id',
                    'index',
                    'image'
                ]

    def save_model(self, request, obj, form, change):
        ''' checks if the behsa offer id of a Reward has changed. if it has changed, it soft-deletes
            the old Reward'''

        if not change:
            return super().save_model(request, obj, form, change)
        old_obj = Reward.objects.all_with_deleted().filter(id=obj.id).first()
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

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """
        return {}


class RewardInline(nested_admin.NestedTabularInline):
    model = Reward
    extra = 0

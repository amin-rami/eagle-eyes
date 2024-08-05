from django.contrib import admin
import nested_admin
from eagle_eyes.apps.referral.models import ReferralCriteria


@admin.register(ReferralCriteria)
class ReferralCriteriaAdmin(admin.ModelAdmin):
    list_display = (
        'reward_criteria',
        'referee_required_action',
        'value',
        'referee_rewarded_action',
    )

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """
        return {}


class ReferralCriteriaInline(nested_admin.NestedTabularInline):
    model = ReferralCriteria
    extra = 0

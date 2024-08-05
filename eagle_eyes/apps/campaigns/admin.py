from django.contrib import admin
from eagle_eyes.apps.campaigns.models import (
    Vertical,
    Action,
    ActionParameter,
    Campaign,
    RewardCriteria,
    Stage,
    CampaignCheckpoint
)
from eagle_eyes.apps.referral_reward.admin import RewardInline
from eagle_eyes.apps.referral.admin import ReferralCriteriaInline
from eagle_eyes.apps.campaigns.forms import ActionInlineFormSet, CriteriaInlineFormSet, StageInlineFormSet
from django.utils import timezone
import nested_admin


class RewardCriteriaInline(nested_admin.NestedTabularInline):
    inlines = [ReferralCriteriaInline]
    model = RewardCriteria
    extra = 0
    formset = CriteriaInlineFormSet

    def has_add_permission(self, request, obj=None):
        # If campaign is started, do not permit adding new criteria to stages
        now = timezone.now()
        if isinstance(obj, Stage) and obj is not None and obj.pk is not None and obj.campaign.start_date <= now:
            return False
        return super().has_add_permission(request, obj)


class StageInline(nested_admin.NestedStackedInline):
    inlines = [RewardCriteriaInline]
    model = Stage
    extra = 0
    formset = StageInlineFormSet

    def has_add_permission(self, request, obj=None):
        # If campaign is started, do not permit adding new stages
        now = timezone.now()
        if obj is not None and obj.pk is not None and obj.start_date <= now:
            return False
        return super().has_add_permission(request, obj)


class CampaignCheckpointInline(nested_admin.NestedStackedInline):
    model = CampaignCheckpoint
    inlines = [RewardInline]
    extra = 0


class ActionParameterInline(nested_admin.NestedTabularInline):
    model = ActionParameter
    extra = 0


class ActionInline(nested_admin.NestedTabularInline):
    inlines = [ActionParameterInline]
    model = Action
    extra = 0
    formset = ActionInlineFormSet

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Vertical)
class VerticalAdmin(nested_admin.NestedModelAdmin):
    inlines = [ActionInline]
    list_display = (
        'id',
        'name',
    )
    list_display_links = (
        'name',
    )

    def get_readonly_fields(self, request, obj=None):

        if obj:
            return ('name', )

        return super().get_readonly_fields(request, obj)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """
        return {}


@admin.register(ActionParameter)
class ActionParameterAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """

        return {}


@admin.register(Campaign)
class CampaignAdmin(nested_admin.NestedModelAdmin):

    inlines = [StageInline, CampaignCheckpointInline]
    add_form_template = change_form_template = 'campaigns/campaign_add_change_form.html'

    list_display = (
        'id',
        'title',
        'reward_type',
        'start_date',
        'end_date',
    )

    list_filter = (
        'start_date',
        'end_date',
    )

    list_display_links = (
        'id',
        'title',
    )


@admin.register(CampaignCheckpoint)
class CampaignCheckpointAdmin(admin.ModelAdmin):

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """

        return {}


@admin.register(RewardCriteria)
class RewardCriteriaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'stage',
    )

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """

        return {}


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):

    def get_model_perms(self, request):
        """
        Hide model to prevent implicit editing
        """
        return {}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'campaign':
            kwargs["queryset"] = Campaign.objects.filter(
                start_date__gt=timezone.now()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.campaign.is_active:
    #         return False
    #     return True

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return obj.campaign.start_date > timezone.now()
        return super().has_change_permission(request, obj)

from django import forms
from django.utils import timezone


class ActionInlineFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        """
        Prevent admin from accidentally removing an action if it has an active campaign.
        """
        super().add_fields(form, index)
        action = form.instance
        now = timezone.now()
        if action is not None and action.pk is not None and action.reward_criterias.filter(
            stage__campaign__start_date__lte=now,
            stage__campaign__end_date__gte=now
        ).exists():
            form.fields['DELETE'].disabled = True


class StageInlineFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        """
        Prevent admin from accidentally removing stages of an started campaign.
        """
        super().add_fields(form, index)
        stage = form.instance
        now = timezone.now()
        if stage is not None and stage.pk is not None and stage.campaign.start_date <= now:
            form.fields['DELETE'].disabled = True


class CriteriaInlineFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        """
        Prevent admin from accidentally removing criteria of an started campaign.
        """
        super().add_fields(form, index)
        criteria = form.instance
        now = timezone.now()
        if criteria is not None and criteria.pk is not None and criteria.stage.campaign.start_date <= now:
            form.fields['DELETE'].disabled = True

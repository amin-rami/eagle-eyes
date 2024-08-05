from django.db import models
from eagle_eyes.apps.campaigns.models import Action, RewardCriteria


class Referral(models.Model):
    referrer_phone_number = models.CharField(max_length=20)
    referee_phone_number = models.CharField(max_length=20)
    created_time = models.DateTimeField()
    done = models.BooleanField(default=False)
    done_time = models.DateTimeField(null=True)


class ReferralState(models.Model):
    referral = models.ForeignKey(to=Referral, on_delete=models.CASCADE, related_name="referrals")
    state = models.JSONField(null=True)


class ReferralCriteria(models.Model):
    reward_criteria = models.ForeignKey(to=RewardCriteria, on_delete=models.CASCADE, related_name="referral_criterias")
    referee_required_action = models.ForeignKey(
                                                to=Action,
                                                on_delete=models.CASCADE,
                                                related_name="referral_criterias_required",
                                                null=True
                                            )
    referee_rewarded_action = models.ForeignKey(
                                                to=Action,
                                                on_delete=models.CASCADE,
                                                related_name="referral_criterias_rewarded",
                                                null=True
                                            )
    value = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.referee_required_action.vertical.name} - {self.referee_required_action.title}"

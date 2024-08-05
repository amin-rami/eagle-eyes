from rest_framework import serializers
from eagle_eyes.apps.campaigns.models import Campaign
from eagle_eyes.apps.referral_reward import exceptions


class ValidateSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()

    def validate(self, data):
        if not Campaign.objects.filter(id=data["campaign_id"]).exists():
            raise exceptions.CampaignNotFound()
        return data


class ReferralSerializer(serializers.Serializer):
    referrer = serializers.CharField()
    referee = serializers.CharField()

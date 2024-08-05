from rest_framework import serializers
from eagle_eyes.apps.referral.models import Referral
from eagle_eyes.apps.eagleusers.services import UserService


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'


class ReferralSubmissionSerializer(serializers.Serializer):
    referrer = serializers.CharField()
    referee = serializers.CharField(allow_blank=True)

    def validate(self, data):
        data["referee"] = UserService.format_phone_number(data["referee"])
        return data


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, data):
        data['phone_number'] = UserService.format_phone_number(data['phone_number'])
        return data

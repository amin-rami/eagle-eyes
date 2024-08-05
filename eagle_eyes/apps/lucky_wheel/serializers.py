from urllib.parse import urlparse
from rest_framework import serializers
from eagle_eyes.apps.behsa.v1.exceptions import DataNotValid
from eagle_eyes.apps.lucky_wheel.models import LuckyWheel


class LuckyWheelSerializer(serializers.ModelSerializer):
    def get_image_path(self, obj) -> str:
        url = urlparse(obj.slice_image.url)
        return url.path

    slice_image_path = serializers.SerializerMethodField(method_name='get_image_path')

    class Meta:
        model = LuckyWheel
        fields = (
            'id',
            'title',
            'slice_image_path',
            'client_index',
            'after_spin_title',
            'after_spin_description',
            'campaign',
        )


class LuckyWheelQueryParamsSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()


class UserCampaignSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    campaign_id = serializers.IntegerField()
    phone_number = serializers.CharField()

    def validate(self, data):
        if len(data['phone_number']) != 10 or str(data['phone_number'][0]) != '9':
            raise DataNotValid()
        return data


class ValidationTokenSerializer(serializers.Serializer):
    val_token = serializers.CharField(max_length=1000)
    salt_token = serializers.CharField(max_length=1000)

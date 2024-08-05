from pydoc import locate
from rest_framework import serializers, exceptions
from eagle_eyes.apps.campaigns.models import Action, ActionParameter, CampaignState, CampaignCheckpoint, Campaign
from eagle_eyes.apps.campaigns.services import CampaignStateService
from eagle_eyes.apps.referral.models import Referral
from eagle_eyes.apps.eagleusers.services import UserService
from urllib.parse import urlparse
from uuid import UUID


class EventSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=256, required=False, allow_blank=True, allow_null=True)
    vertical = serializers.CharField(max_length=100)
    action = serializers.CharField(max_length=100)
    params = serializers.JSONField(default=dict)
    date_time = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        # Unauthorized
        try:
            if len(str(data.get('user_id'))) != 36:
                raise Exception
            UUID(data.get('user_id'))
        except Exception:
            raise exceptions.AuthenticationFailed()
        # Check requested action and vertical exists
        try:
            action = Action.objects.get(title=data['action'], vertical__name=data['vertical'])
        except Action.DoesNotExist:
            raise serializers.ValidationError("Action or Vertical does not exist.")

        for key, value in data['params'].items():
            # Check if parameter with the given key exists
            try:
                action_param = ActionParameter.objects.get(action=action, key=key)
            except ActionParameter.DoesNotExist:
                raise serializers.ValidationError(
                    f"Parameter with key '{key}' is not defined for action '{action.title}'."
                )

            # Check type & convert parameter value
            try:
                data['params'][key] = locate(action_param.value_type)(value)
            except ValueError:
                raise serializers.ValidationError(
                    f"Parameter value with key '{key}' is not a valid '{action_param.value_type}'."
                )

        return data


class CampaignCheckpointSerializer(serializers.ModelSerializer):
    def get_image_path(self, obj) -> str:
        try:
            url = urlparse(obj.image.url)
            return url.path
        except ValueError:
            return ''

    checkpoint_image = serializers.SerializerMethodField(method_name='get_image_path')

    class Meta:
        model = CampaignCheckpoint
        extra_fields = ('checkpoint_image', )
        exclude = ('image', )


class CampaignStateListSerializer(serializers.ModelSerializer):
    def get_image_path(self, obj) -> str:
        try:
            url = urlparse(obj.campaign.image.url)
            return url.path
        except ValueError:
            return ''

    def get_no_chance_image_path(self, obj) -> str:
        try:
            url = urlparse(obj.campaign.no_chance_image.url)
            return url.path
        except ValueError:
            return ''

    def get_has_win_chance(self, obj) -> bool:
        return CampaignStateService.has_win_chance(obj)

    def get_pecentage(self, obj) -> int:
        return CampaignStateService.get_current_percentage(obj)

    def get_is_referee(self, obj):
        campaign = obj.campaign
        if campaign.campaign_type != str(Campaign.CampaignType.REFEREE):
            return False
        phone_number = UserService.phone_number(obj.user_id)
        return Referral.objects.filter(referee_phone_number=phone_number).exists()

    checkpoints = CampaignCheckpointSerializer(source='campaign.checkpoints', many=True)
    campaign_title = serializers.CharField(source='campaign.title')
    campaign_image = serializers.SerializerMethodField(method_name='get_image_path')
    has_win_chance = serializers.SerializerMethodField(method_name='get_has_win_chance')
    start_date = serializers.DateTimeField(source='campaign.start_date')
    end_date = serializers.DateTimeField(source='campaign.end_date')
    lottery_date = serializers.DateField(source='campaign.lottery_date')
    lottery_text = serializers.CharField(source='campaign.lottery_text')
    no_chance_image = serializers.SerializerMethodField(method_name='get_no_chance_image_path')
    reward_type = serializers.CharField(source='campaign.reward_type')
    campaign_type = serializers.CharField(source='campaign.campaign_type')
    percentage = serializers.SerializerMethodField(method_name='get_pecentage')
    is_referee = serializers.SerializerMethodField(method_name='get_is_referee')

    class Meta:
        model = CampaignState
        fields = '__all__'
        extra_fields = (
            'campaign_title',
            'campaign_image',
            'has_win_chance',
        )


class CampaignStateListQueryParamSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(required=False)


class ActionParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActionParameter
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):

    params_list = ActionParameterSerializer(source='params', many=True)

    class Meta:
        model = Action
        fields = '__all__'

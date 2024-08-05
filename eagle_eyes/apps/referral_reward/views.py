from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from eagle_eyes.apps.referral_reward import serializers
from eagle_eyes.apps.referral_reward.services import RewardServices
from eagle_eyes.apps.eagleusers.services import UserService
from eagle_eyes.apps.campaigns.models import Campaign
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


class Validate(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        parameters=[
            serializers.ValidateSerializer
        ])
    def get(self, request, version):
        serializer = serializers.ValidateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        campaign_id = serializer.validated_data["campaign_id"]
        user_id = UserService.extract_user_id(request)
        campaign = Campaign.objects.get(id=campaign_id)
        resp_data = RewardServices.gather_rewards_info(user_id, campaign)
        return Response(resp_data, status=status.HTTP_200_OK)


class Allocate(APIView):
    authentication_classes = ()
    permission_classes = ()

    @transaction.atomic
    def post(self, request, version):
        reward_token = request.headers.get('Reward-Token')
        auth_token = request.headers.get('X-Auth-Token')
        user_id = UserService.extract_user_id(request)
        auth_id = request.data.get('userid') or user_id

        # separate self logged in users with third party
        if not auth_token:
            phone_number = UserService.phone_number(user_id)
            auth_number = UserService.phone_number(auth_id)
        else:
            phone_number = None
            auth_number = UserService.extract_auth_phone_number(auth_token)

        payload = RewardServices.validate_token(user_id, reward_token)
        RewardServices.check_active_reward(auth_number, payload["reward_id"])

        user_reward = RewardServices.create_user_reward(
            user_id,
            payload["reward_id"],
            auth_number,
            payload["is_mci"],
            phone_number
        )
        RewardServices.allocate(user_id, user_reward.reward.offer_id, auth_token)
        user_reward.save()
        cache.delete(RewardServices.generate_key(payload["user_id"], payload["reward_id"]))

        user_reward.save()
        resp_data = {
            "reward": user_reward.reward.title
        }

        return Response(resp_data, status=status.HTTP_201_CREATED)

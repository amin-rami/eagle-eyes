from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from eagle_eyes.apps.lucky_wheel.serializers import (
    LuckyWheelQueryParamsSerializer,
    LuckyWheelSerializer,
    ValidationTokenSerializer,
    UserCampaignSerializer,
    )
from eagle_eyes.apps.lucky_wheel.services import LuckyWheelService, get_behsa
from drf_spectacular.utils import extend_schema

behsa_api = get_behsa()


class LuckyWheelList(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        parameters=[
          LuckyWheelQueryParamsSerializer
        ],
        responses={200: LuckyWheelQueryParamsSerializer},
    )
    def get(self, request, version):
        query_params = LuckyWheelQueryParamsSerializer(data=request.query_params)
        if not query_params.is_valid():
            return Response(data=query_params.errors, status=status.HTTP_400_BAD_REQUEST)

        campaign_id = query_params.validated_data.get('campaign_id')
        slices = LuckyWheelService.list_slices(campaign_id=campaign_id)
        serializer = LuckyWheelSerializer(slices, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Validate(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=UserCampaignSerializer,
        responses={200: ValidationTokenSerializer}
    )
    def post(self, request, version):
        serializer = UserCampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]
        campaign_id = serializer.validated_data["campaign_id"]

        LuckyWheelService.validate_user_campaign(user_id, campaign_id)
        user_detail = LuckyWheelService.behsa_validate(request)
        LuckyWheelService.check_active_rewards(request, user_detail.salt_token)

        payload = {
            'user_id': user_id,
            'campaign_id': campaign_id,
            'phone_number': user_detail.phone_detail.number,
            'is_mci': user_detail.phone_detail.is_mci
        }
        expire = 60 * 5
        val_token = LuckyWheelService.create_token(payload, expire)
        cache.set(f"authorize:{user_id}", val_token, timeout=expire)
        resp = {
            'val_token': val_token,
            'salt_token': user_detail.salt_token
        }

        return Response(resp)


class Allocate(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        responses={200: LuckyWheelSerializer}
    )
    @transaction.atomic
    def get(self, request, version):
        val_token = request.headers.get('Authorization')
        auth_token = request.headers.get('x_auth_token')
        salt_token = request.headers.get('x_salt_token')

        data = LuckyWheelService.validate_token(val_token)
        slices = LuckyWheelService.list_slices(campaign_id=data["campaign_id"]).all()
        reward = LuckyWheelService.allocate_reward(slices)
        behsa_api.chance_activation(auth_token, salt_token, reward.behsa_offer_id)
        LuckyWheelService.create_user_reward(data["user_id"], reward)
        serializer = LuckyWheelSerializer(reward)
        return Response(serializer.data)

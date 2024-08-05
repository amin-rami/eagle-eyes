from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from eagle_eyes.apps.campaigns import serializers
from eagle_eyes.apps.campaigns.dependencies import get_streamer
from eagle_eyes.apps.campaigns.models import Action, Campaign, CampaignState
from eagle_eyes.apps.campaigns.services import CampaignStateService
from eagle_eyes.apps.eagleusers.services import UserService
from eagle_eyes.settings.project import CAMPAIGNS_DEPRECATION_DATE


class CampaignStateList(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        parameters=[
            serializers.CampaignStateListQueryParamSerializer
        ],
        responses={200: serializers.CampaignStateListSerializer},
    )
    def get(self, request, version):
        # Get query parameters and validate
        query_param_serializer = serializers.CampaignStateListQueryParamSerializer(
            data=request.query_params
        )
        if not query_param_serializer.is_valid():
            return Response(data=query_param_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        campaign_id = query_param_serializer.validated_data.get('campaign_id')
        user_id = UserService.extract_user_id(request)

        # If campaign_id is None (not sent), then return all the `active` campaign for the user
        if campaign_id is None:
            current_datetime = timezone.now()
            campaigns = Campaign.objects.filter(
                start_date__lte=current_datetime
            )
            if CAMPAIGNS_DEPRECATION_DATE:
                campaigns = campaigns.filter(
                    end_date__gt=CAMPAIGNS_DEPRECATION_DATE
                )
            campaign_states = [
                CampaignStateService.get_or_create_in_memory(user_id=user_id, campaign=campaign)
                for campaign in campaigns
            ]
            campaign_states = [
                campaign_state for campaign_state in campaign_states
                if CampaignStateService.is_referee(campaign_state)
                or campaign_state.campaign.campaign_type != Campaign.CampaignType.REFEREE
            ]
        else:
            # If campaign state is given, return the user's state in the campaign
            campaign_states = CampaignState.objects.filter(
                campaign_id=campaign_id,
                user_id=user_id
            )

        campaign_states_with_config = sorted([
            CampaignStateService.inject_campaign_config(campaign_state)
            for campaign_state in campaign_states
        ], key=lambda cs: cs.campaign.index)
        serializer_ = serializers.CampaignStateListSerializer(campaign_states_with_config, many=True)
        return Response(data=serializer_.data)


class EventList(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=serializers.EventSerializer,
        responses={201: serializers.EventSerializer},
    )
    def post(self, request, version):
        user_id = UserService.extract_user_id(request)
        ad_id = request.headers.get("X-Ad-ID")
        request_data = request.data.copy()
        request_data['user_id'] = user_id if user_id else request.data.get('user_id')
        event_serializer = serializers.EventSerializer(data=request_data)
        if not event_serializer.is_valid():
            return Response(data=event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = dict(event_serializer.data)
        data['date_time'] = str(timezone.now())
        data['ad_id'] = ad_id
        get_streamer().send(data=data)
        return Response(data=data, status=status.HTTP_201_CREATED)


class ActionDetails(RetrieveAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.ActionSerializer
    queryset = Action.objects.all()

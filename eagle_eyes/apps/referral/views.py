from eagle_eyes.apps.referral.models import Referral
from eagle_eyes.apps.referral import serializers
from eagle_eyes.apps.referral import exceptions
from eagle_eyes.apps.referral.services import MutualEventServices
from eagle_eyes.apps.eagleusers.services import UserService
from eagle_eyes.apps.campaigns.management.commands.decrypt_user_id import decrypt_user_id
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema
import datetime
import os


class ReferralSubmission(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=serializers.ReferralSubmissionSerializer,
        )
    def post(self, request, version):
        serializer = serializers.ReferralSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # backward compatible (duo to linkes shared before)
        referrer = serializer.validated_data["referrer"]
        if len(referrer) == 32:
            referrer_phone_number = decrypt_user_id(referrer)
        else:
            referrer_phone_number = UserService.phone_number(referrer)
        if not referrer_phone_number:
            raise exceptions.InvalidInvitationLink()
        referee_phone_number = serializer.validated_data["referee"]
        now = timezone.now()

        if referrer_phone_number == referee_phone_number:
            raise exceptions.SelfInvite()
        if Referral.objects.filter(referrer_phone_number=referee_phone_number).exists():
            raise exceptions.AlreadySignedUp()

        old_referral = Referral.objects.filter(referee_phone_number=referee_phone_number).first()
        new_referral = Referral(
            referrer_phone_number=referrer_phone_number,
            referee_phone_number=referee_phone_number,
            created_time=now,
            done=False,
        )

        if old_referral:
            if old_referral.created_time > now - datetime.timedelta(days=3) or old_referral.done:
                raise exceptions.AlreadyInvited()
            old_referral.delete()
        new_referral.save()

        _serializer = serializers.ReferralSerializer(new_referral)
        return Response(
            data=_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ReferralLogin(APIView):

    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
            request=serializers.LoginSerializer,
    )
    def post(self, request, version):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        referral = Referral.objects.filter(referee_phone_number=phone_number, done=False).first()
        if referral:
            referral.done = True
            referral.done_time = timezone.now()
            referrer_event = {
                'action': os.getenv('REFERRER_ACTION', 'referrer_done'),
                'vertical': os.getenv('REFERRER_VERTICAL', 'referral')
            }
            referee_event = {
                'action': os.getenv('REFEREE_ACTION', 'referee_done'),
                'vertical': os.getenv('REFEREE_VERTICAL', 'referral')
            }
            MutualEventServices.send_mutual_event(referral, referrer_event, referee_event)
            referral.save()
        return Response(
            status=status.HTTP_202_ACCEPTED
        )

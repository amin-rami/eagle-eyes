from eagle_eyes.apps.eagleusers.services import UserService
from eagle_eyes.apps.club.models import UserState
from eagle_eyes.apps.club.serializers import UserStateSerializer

from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist


class UserStateList(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, version):

        user_id = UserService.extract_user_id(request)
        if user_id is None:
            raise exceptions.NotAuthenticated()

        try:
            user_state = UserState.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            user_state = UserState(
                user_id=user_id
            )

        serilaizer = UserStateSerializer(user_state)
        return Response(serilaizer.data)

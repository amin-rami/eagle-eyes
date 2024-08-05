from django.http import Http404
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from eagle_eyes.apps.games import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from eagle_eyes.apps.games.models import UserState
from eagle_eyes.apps.eagleusers.services import UserService


class UserStateList(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        parameters=[
            serializers.UserStateListQueryParamSerializer
        ],
        responses={200: serializers.UserStateListSerializer},
    )
    def get(self, request, version):
        user_id = UserService.extract_user_id(request)
        if user_id is None:
            query_param_serializer = serializers.UserStateListQueryParamSerializer(
                data=request.query_params
            )
            if not query_param_serializer.is_valid():
                return Response(
                    data=query_param_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_id = query_param_serializer.validated_data.get('user_id')
        try:
            user_state = UserState.objects.get(user_id=user_id)
        except UserState.DoesNotExist:
            raise Http404
        serializer_ = serializers.UserStateListSerializer(user_state)
        return Response(data=serializer_.data)


class UserTopRanksList(ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = UserState.objects.filter().order_by('-level')[:20]
    serializer_class = serializers.UserStateListSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

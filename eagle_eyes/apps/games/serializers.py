from rest_framework import serializers

from eagle_eyes.apps.games.models import UserState


class UserStateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserState
        fields = '__all__'


class UserStateListQueryParamSerializer(serializers.Serializer):
    user_id = serializers.CharField()

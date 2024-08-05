from eagle_eyes.apps.club.models import UserState, Level

from rest_framework import serializers


class UserStateSerializer(serializers.ModelSerializer):

    def get_current_level(self, obj):
        level = Level.objects.filter(start_xp__lte=obj.XP).order_by('-start_xp').first()
        return [level.start_xp, level.title]

    def get_next_level(self, obj):
        level = Level.objects.filter(start_xp__gt=obj.XP).order_by('start_xp').first()
        return [level.start_xp, level.title]

    current_level = serializers.SerializerMethodField(method_name='get_current_level')
    next_level = serializers.SerializerMethodField(method_name='get_next_level')

    class Meta:
        model = UserState
        fields = (
            'XP',
            'points',
            'current_level',
            'next_level'
        )

from eagle_eyes.apps.campaigns.models import Action
from django.db import models


class Mission(models.Model):
    title = models.CharField(max_length=1024)
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='missions')
    index = models.PositiveSmallIntegerField()
    XP = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    hyperlink = models.URLField(blank=True, null=True)
    has_limit = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.action.title} - {self.action.vertical.name}"


class Booster(models.Model):
    mission = models.ForeignKey(to=Mission, on_delete=models.CASCADE, related_name='boosters')
    multiplier = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class UserState(models.Model):
    user_id = models.CharField(primary_key=True)
    XP = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)


class Level(models.Model):
    title = models.CharField()
    start_xp = models.PositiveIntegerField()


class Config(models.Model):
    title = models.CharField(max_length=1024)
    value = models.CharField(max_length=4096)


class ActivityHistory(models.Model):
    user_id = models.CharField()
    mission_id = models.PositiveIntegerField()
    vertical = models.CharField()
    action = models.CharField()
    earned_xp = models.PositiveIntegerField()
    earned_points = models.PositiveIntegerField()
    date_time = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'date_time']),
        ]

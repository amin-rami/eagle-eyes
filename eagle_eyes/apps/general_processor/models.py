from django.db import models
from eagle_eyes.apps.campaigns.models import Action


class Tracker(models.Model):
    title = models.CharField(max_length=1024)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title}"


class EngagementCriteria(models.Model):
    tracker = models.ForeignKey(to=Tracker, on_delete=models.CASCADE, related_name='engagement_criterias')
    action = models.ForeignKey(to=Action, on_delete=models.CASCADE, related_name='engagement_criterias')
    value = models.PositiveSmallIntegerField()


class EngagementState(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='states')
    user_id = models.CharField(max_length=100)
    state = models.JSONField(null=True)
    done = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    started = models.DateTimeField(null=True)
    finished = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)

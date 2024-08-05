from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.forms import ValidationError
from django_prometheus.models import ExportModelOperationsMixin
from django.core.validators import MaxValueValidator
from safedelete.models import SafeDeleteModel
from safedelete import SOFT_DELETE_CASCADE
from eagle_eyes.utils import AmazonS3ImageStorage
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class Vertical(SafeDeleteModel):
    name = models.CharField(max_length=100)
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name'],
                condition=models.Q(deleted__isnull=True),
                name='unique_name'
            )
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if Vertical.objects.filter(name=self.name).exists() and (self.id is None):
            raise ValidationError(f'Vertical with name {self.name} already exists')


class Action(ExportModelOperationsMixin('action'), SafeDeleteModel):
    title = models.CharField(max_length=100)
    vertical = models.ForeignKey(Vertical, on_delete=models.CASCADE, related_name='actions')
    child_actions = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="parent_actions")

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['vertical', 'title'],
                condition=models.Q(deleted__isnull=True),
                name='unique_vertical_and_title'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.vertical}'

    def clean(self):
        if Action.objects.filter(vertical=self.vertical, title=self.title).exists() and (self.id is None):
            raise ValidationError(f'Action with title {self.title} and vertical {self.vertical} already exists')


class ActionParameter(ExportModelOperationsMixin('action_parameters'), models.Model):
    class ParamValueType(models.TextChoices):
        STR = 'str', _('string')
        INT = 'int', _('integer')
        FLOAT = 'float', _('float')

    action = models.ForeignKey(
        to=Action,
        on_delete=models.CASCADE,
        related_name='params'
    )
    key = models.CharField(max_length=128)
    value_type = models.CharField(
        max_length=10,
        choices=ParamValueType.choices,
        default=ParamValueType.FLOAT
    )

    class Meta:
        unique_together = (
            ('action', 'key'),
        )


class Event(ExportModelOperationsMixin('event'), SafeDeleteModel):
    user = models.CharField(
        max_length=512
    )
    action = models.ForeignKey(
        to=Action,
        on_delete=models.CASCADE
    )
    params = models.JSONField()
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.action.vertical.name}-{self.action.title}-{self.user}"


class Campaign(ExportModelOperationsMixin('campaign'), SafeDeleteModel):
    class RewardType(models.TextChoices):
        LOTTERY = ("LOTTERY", "lottery")
        INTERNET = ("INTERNET", "internet")

    class ProgressType(models.TextChoices):
        STAGE_STATE = ("STAGE_STATE", "stage state")
        REWARD_CRITERIA_STATE = ("REWARD_CRITERIA_STATE", "reward criteria state")
        REWARD_CRITERIA_VALUE = ("REWARD_CRITERIA_VALUE", "reward criteria value")
        MIN_CRITERIA_VALUE = ("MIN_CRITERIA_VALUE", "min criteria value")

    class CampaignType(models.TextChoices):
        REGULAR = ("REGULAR", "regular")
        REFERRAL = ("REFERRAL", "referral")
        REFEREE = ("REFEREE", "referee")
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    index = models.SmallIntegerField(default=0)
    campaign_type = models.CharField(
        max_length=60,
        choices=CampaignType.choices,
        default=CampaignType.REGULAR
    )
    reward_type = models.CharField(
        max_length=20,
        choices=RewardType.choices,
        default=RewardType.LOTTERY,
    )
    progress_type = models.CharField(
        max_length=60,
        choices=ProgressType.choices,
        default=ProgressType.REWARD_CRITERIA_STATE
    )
    lottery_date = models.DateField(null=True, blank=True)
    lottery_text = models.TextField(null=True, blank=True)
    no_chance_image = models.ImageField(
        storage=AmazonS3ImageStorage,
        null=True
    )
    image = models.ImageField(
        storage=AmazonS3ImageStorage,
        null=True
    )
    _safedelete_policy = SOFT_DELETE_CASCADE

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.start_date <= timezone.now() <= self.end_date


class CampaignCheckpoint(ExportModelOperationsMixin('stage'), models.Model):
    campaign = models.ForeignKey(to=Campaign, on_delete=models.CASCADE, related_name='checkpoints')
    image = models.ImageField(
        storage=AmazonS3ImageStorage,
        null=True
    )
    text_done = models.TextField()
    text_undone = models.TextField()
    percentage = models.PositiveSmallIntegerField(
        default=50,
        validators=[MaxValueValidator(100)]
    )
    rewarded_chances = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = (
            ('campaign', 'percentage'),
        )

    def __str__(self):
        return f"{self.campaign.title} - percentage: {self.percentage}%"


class Stage(ExportModelOperationsMixin('stage'), SafeDeleteModel):
    campaign = models.ForeignKey(to=Campaign, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=128)
    index = models.PositiveSmallIntegerField()
    delay = models.DurationField(
        null=True,
        blank=True,
        default=timezone.timedelta(days=0)
    )

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['campaign', 'index'],
                condition=models.Q(deleted__isnull=True),
                name='unique_campaign_index'
            )
        ]

    def clean(self):
        if Stage.objects.filter(campaign=self.campaign, index=self.index).exists() and self.id is None:
            raise ValidationError(
                f'''Stage with campaign {self.campaign}, index {self.index} already exists'''
            )

    @property
    def is_start_time_reached(self):
        start_time = self.campaign.start_date
        previous_stages_total_duration = self.campaign.stages.filter(index__lt=self.index).aggregate(Sum('delay'))
        if previous_stages_total_duration['delay__sum']:
            start_time += previous_stages_total_duration['delay__sum']
        return timezone.now() >= start_time

    def __str__(self):
        return f'{self.campaign}-{self.index}'


class RewardCriteria(ExportModelOperationsMixin('reward_criteria'), SafeDeleteModel):
    stage = models.ForeignKey(to=Stage, on_delete=models.CASCADE, related_name='reward_criterias')
    action = models.ForeignKey(to=Action, on_delete=models.CASCADE, related_name='reward_criterias')
    param = models.CharField(max_length=200, blank=True, null=True)
    value = models.FloatField(default=0)
    score = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=512)
    hyperlink = models.URLField(blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['stage', 'action', 'param'],
                condition=models.Q(deleted__isnull=True),
                name='unique_stage_action_param'
            )
        ]

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if RewardCriteria.objects.filter(
            stage=self.stage, action=self.action, param=self.param
        ).exists() and self.id is None:
            raise ValidationError(f'''Reward Criteria with
                action {self.action},
                stage {self.stage},
                param {self.param},
                already exists''')


class CampaignState(ExportModelOperationsMixin('campaign_state'), SafeDeleteModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='states')
    user_id = models.CharField(max_length=100)
    state = models.JSONField(null=True)
    done = models.BooleanField(default=False)
    started = models.DateTimeField(null=True)
    finished = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('campaign', 'user_id'),
                condition=models.Q(deleted__isnull=True),
                name='unique_campaign_userid'
            )
        ]

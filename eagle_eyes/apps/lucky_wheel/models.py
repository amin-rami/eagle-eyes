from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete import HARD_DELETE_NOCASCADE
from eagle_eyes.apps.campaigns.models import Campaign
from eagle_eyes.utils import AmazonS3ImageStorage


class LuckyWheel(SafeDeleteModel):
    campaign = models.ForeignKey(to=Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slice_image = models.ImageField(storage=AmazonS3ImageStorage, max_length=500)
    behsa_offer_id = models.CharField(max_length=100, null=True, blank=True)
    client_index = models.IntegerField(default=1)
    chance = models.FloatField(
        help_text="شانس برنده شدن هر کاربر نسبت به باقی جایزه ها. یک عدد بین ۰ تا ۱۰۰"
    )
    limit = models.PositiveIntegerField(
        help_text="تعداد مجاز برنده شدن این جایزه در کمپین",
        null=True
    )
    after_spin_title = models.CharField(max_length=255, null=True, blank=True)
    after_spin_description = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name="active")
    _safedelete_policy = HARD_DELETE_NOCASCADE

    def __str__(self):
        return f"{self.title} - {self.campaign}"


class UserReward(models.Model):
    user_id = models.CharField(max_length=256)
    slice = models.ForeignKey(to=LuckyWheel, on_delete=models.CASCADE)
    date_time = models.DateTimeField()

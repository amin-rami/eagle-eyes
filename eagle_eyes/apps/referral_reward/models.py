from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete import HARD_DELETE_NOCASCADE
from eagle_eyes.apps.campaigns.models import CampaignCheckpoint
from eagle_eyes.utils import AmazonS3ImageStorage
from urllib.parse import urlparse


class Reward(SafeDeleteModel):
    title = models.CharField(max_length=1024, null=True)
    description = models.TextField(null=True)
    checkpoint = models.ForeignKey(to=CampaignCheckpoint, on_delete=models.CASCADE, related_name="reward")
    offer_id = models.CharField(max_length=1024)
    index = models.SmallIntegerField(default=0)
    image = models.ImageField(storage=AmazonS3ImageStorage, null=True)
    _safedelete_policy = HARD_DELETE_NOCASCADE

    def __str__(self):
        return f"{self.title} - {self.checkpoint.campaign.title}"

    @property
    def get_image_url(self):
        try:
            url = urlparse(self.image.url)
            return url.path
        except ValueError:
            return ''


class UserReward(SafeDeleteModel):
    user_id = models.CharField(max_length=1024)
    phone_number = models.CharField(max_length=20, null=True)
    auth_number = models.CharField(max_length=20, null=True)
    reward = models.ForeignKey(to=Reward, on_delete=models.CASCADE, related_name="user_rewards")
    date_time = models.DateTimeField()
    is_mci = models.BooleanField(default=True)

from django.contrib.auth.models import AbstractUser
from django.db import models


class Config(models.Model):
    title = models.CharField(max_length=1024, null=True)
    value = models.TextField(null=True)

    def __str__(self):
        return f"{self.title}"


class EagleUser(AbstractUser):
    pass


class Notary(models.Model):
    user_id = models.CharField(max_length=36, primary_key=True)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return self.phone_number

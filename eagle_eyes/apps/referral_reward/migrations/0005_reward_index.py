# Generated by Django 4.2 on 2023-05-13 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral_reward', '0004_referral_referralstate_referralcriteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='index',
            field=models.SmallIntegerField(default=0),
        ),
    ]

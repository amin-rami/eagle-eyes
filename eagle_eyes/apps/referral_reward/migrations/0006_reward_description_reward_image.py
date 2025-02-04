# Generated by Django 4.2 on 2023-05-13 21:33

from django.db import migrations, models
import eagle_eyes.utils


class Migration(migrations.Migration):

    dependencies = [
        ('referral_reward', '0005_reward_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='reward',
            name='image',
            field=models.ImageField(null=True, upload_to='', verbose_name=eagle_eyes.utils.AmazonS3ImageStorage),
        ),
    ]

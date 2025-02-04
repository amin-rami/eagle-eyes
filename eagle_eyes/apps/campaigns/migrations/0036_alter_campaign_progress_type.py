# Generated by Django 4.2 on 2023-05-14 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0035_campaign_campaign_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='progress_type',
            field=models.CharField(choices=[('STAGE_STATE', 'stage state'), ('REWARD_CRITERIA_STATE', 'reward criteria state'), ('REWARD_CRITERIA_VALUE', 'reward criteria value'), ('MIN_CRITERIA_VALUE', 'min criteria value')], default='REWARD_CRITERIA_STATE', max_length=60),
        ),
    ]

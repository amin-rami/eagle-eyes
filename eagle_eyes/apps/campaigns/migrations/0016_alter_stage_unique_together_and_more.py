# Generated by Django 4.1.7 on 2023-02-23 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0015_remove_rewardcriteria_unique_campaign_action_param_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stage',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='stage',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('campaign', 'index'), name='unique_campaign_index'),
        ),
    ]

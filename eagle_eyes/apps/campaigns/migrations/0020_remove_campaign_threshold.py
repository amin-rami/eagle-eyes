# Generated by Django 4.1.7 on 2023-03-06 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0019_alter_campaigncheckpoint_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='threshold',
        ),
    ]

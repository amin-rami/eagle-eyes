# Generated by Django 4.1.5 on 2023-01-25 07:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='vertical',
        ),
    ]

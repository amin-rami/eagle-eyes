# Generated by Django 4.1.7 on 2023-03-12 16:40

from django.db import migrations, models
import eagle_eyes.utils


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0026_alter_stage_delay'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='lottery_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='no_chance_image',
            field=models.ImageField(null=True, storage=eagle_eyes.utils.AmazonS3ImageStorage, upload_to=''),
        ),
    ]

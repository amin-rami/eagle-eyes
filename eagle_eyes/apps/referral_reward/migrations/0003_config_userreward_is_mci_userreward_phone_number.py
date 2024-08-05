# Generated by Django 4.2 on 2023-04-26 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral_reward', '0002_reward_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024, null=True)),
                ('value', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='userreward',
            name='is_mci',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userreward',
            name='phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]

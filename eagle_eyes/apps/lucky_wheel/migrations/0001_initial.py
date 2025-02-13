# Generated by Django 4.1.5 on 2023-01-18 05:57

from django.db import migrations, models
import django.db.models.deletion
import eagle_eyes.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LuckyWheelSlice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slice_image', models.ImageField(max_length=500, storage=eagle_eyes.utils.AmazonS3ImageStorage, upload_to='')),
                ('behsa_offer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('client_index', models.IntegerField(default=1)),
                ('chance', models.FloatField(help_text='شانس برنده شدن هر کاربر نسبت به باقی جایزه ها. یک عدد بین ۰ تا ۱۰۰')),
                ('limit', models.PositiveIntegerField(help_text='تعداد مجاز برنده شدن این جایزه در کمپین', null=True)),
                ('after_spin_title', models.CharField(blank=True, max_length=255, null=True)),
                ('after_spin_description', models.CharField(blank=True, max_length=255, null=True)),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaigns.campaign')),
            ],
        ),
    ]

# Generated by Django 5.0.1 on 2024-01-20 13:13

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_room_participants'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
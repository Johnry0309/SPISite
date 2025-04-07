# Generated by Django 5.1.7 on 2025-04-07 08:49

from django.db import migrations, models
from datetime import timedelta  # Import timedelta

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_remove_class_duration_class_duration_per_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='duration_per_day',
        ),
        migrations.AddField(
            model_name='class',
            name='duration',
            field=models.DurationField(default=timedelta(hours=1)),  # Set default to timedelta
        ),
    ]
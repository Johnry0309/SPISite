# Generated by Django 5.1.7 on 2025-04-07 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_remove_class_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='duration',
            field=models.DurationField(),
        ),
    ]

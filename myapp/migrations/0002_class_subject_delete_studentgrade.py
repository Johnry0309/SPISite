# Generated by Django 5.2 on 2025-05-11 09:55

import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='subject',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='myapp.subject'
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='StudentGrade',
        ),
    ]

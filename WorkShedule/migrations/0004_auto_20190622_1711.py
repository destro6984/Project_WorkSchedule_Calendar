# Generated by Django 2.2.2 on 2019-06-22 17:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkShedule', '0003_delete_schedulework'),
    ]

    operations = [
        migrations.AddField(
            model_name='workday',
            name='end_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='workday',
            name='start_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]

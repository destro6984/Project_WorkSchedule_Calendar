# Generated by Django 2.2.2 on 2019-06-26 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkShedule', '0009_auto_20190625_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='workday',
            name='date_free',
            field=models.BooleanField(default=False),
        ),
    ]
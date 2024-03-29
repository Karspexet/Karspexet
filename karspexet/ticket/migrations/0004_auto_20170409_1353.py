# Generated by Django 1.10.1 on 2017-04-09 13:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_auto_20170409_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='finalized',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reservation',
            name='session_timeout',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

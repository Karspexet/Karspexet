# Generated by Django 1.10.1 on 2017-04-09 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('show', '0001_initial'),
        ('ticket', '0004_auto_20170409_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='show',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='show.Show'),
            preserve_default=False,
        ),
    ]

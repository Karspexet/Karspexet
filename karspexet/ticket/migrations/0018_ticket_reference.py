# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-12 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0017_positive_integers_20180322_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='reference',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
# Generated by Django 3.0.6 on 2020-07-11 06:49

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0005_auto_20171209_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='seat_map_dimensions',
            field=django.contrib.postgres.fields.hstore.HStoreField(default=dict),
        ),
    ]

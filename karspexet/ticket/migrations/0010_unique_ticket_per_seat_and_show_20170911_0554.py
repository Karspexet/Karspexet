# Generated by Django 1.10.1 on 2017-09-11 05:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("show", "0001_initial"),
        ("venue", "0002_auto_20170710_1818"),
        ("ticket", "0009_account_phone"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("show", "seat")},
        ),
    ]

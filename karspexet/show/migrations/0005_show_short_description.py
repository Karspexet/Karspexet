# Generated by Django 1.10.1 on 2018-03-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("show", "0004_show_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="show",
            name="short_description",
            field=models.CharField(default="", max_length=255),
        ),
    ]

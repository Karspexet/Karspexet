# Generated by Django 1.10.1 on 2017-12-08 21:32

from django.db import migrations, models

import karspexet.ticket.models


def generate_ticket_codes(apps, schema_editor):
    Ticket = apps.get_model("ticket", "Ticket")
    for row in Ticket.objects.all():
        row.ticket_code = karspexet.ticket.models._generate_random_code()
        row.save()


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0011_reservation_reservation_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="ticket_code",
            field=models.CharField(null=True, max_length=16, unique=True),
        ),
        migrations.RunPython(
            generate_ticket_codes, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="ticket",
            name="ticket_code",
            field=models.CharField(
                default=karspexet.ticket.models._generate_random_code,
                null=False,
                max_length=16,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="reservation_code",
            field=models.CharField(
                default=karspexet.ticket.models._generate_random_code,
                max_length=16,
                unique=True,
            ),
        ),
    ]

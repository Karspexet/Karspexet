# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-02-12 19:12
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0012_ticket_code_20171208_2132'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(5000)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('reservation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ticket.Reservation')),
                ('voucher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ticket.Voucher')),
            ],
        ),
    ]

# Generated by Django 3.2.6 on 2021-08-24 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0019_set_on_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_type',
            field=models.CharField(choices=[('normal', 'Fullpris'), ('student', 'Student'), ('sponsor', 'Sponsor')], default='normal', max_length=10),
        ),
    ]

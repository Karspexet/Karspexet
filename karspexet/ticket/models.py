from django.conf import settings
from django.db import models


# TODO: These should probably all be timestamped


class Reservation(models.Model):
    total = models.IntegerField()


class Ticket(models.Model):
    price = models.IntegerField()


class Voucher(models.Model):
    reservation = models.ForeignKey(Reservation, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    rebate_amount = models.IntegerField(help_text="Rabatt i SEK")

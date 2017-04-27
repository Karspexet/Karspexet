from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models import Q
from django.utils import timezone

from karspexet.show.models import Show
from karspexet.venue.models import Seat


class ActiveReservationsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(session_timeout__gt=timezone.now()) | Q(finalized=True))


class Reservation(models.Model):
    show = models.ForeignKey(Show, null=False)
    total = models.IntegerField()
    tickets = HStoreField()
    session_timeout = models.DateTimeField()
    finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active = ActiveReservationsManager()


class Account(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


class Ticket(models.Model):
    TICKET_TYPES = [
        ("normal", "Fullpris"),
        ("student", "Student"),
    ]
    price = models.IntegerField()
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES, default="normal")
    show = models.ForeignKey(Show, null=False)
    seat = models.ForeignKey(Seat, null=False)
    account = models.ForeignKey(Account, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


class Voucher(models.Model):
    reservation = models.ForeignKey(Reservation, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    rebate_amount = models.IntegerField(help_text="Rabatt i SEK")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

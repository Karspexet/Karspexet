from string import ascii_uppercase, digits
from functools import reduce
from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string

from karspexet.show.models import Show
from karspexet.venue.models import Seat, SeatingGroup

TICKET_TYPES = [
    ("normal", "Fullpris"),
    ("student", "Student"),
]

def _generate_reservation_code():
    return get_random_string(allowed_chars=ascii_uppercase+digits)

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
    reservation_code = models.CharField(unique=True, max_length=16, default=_generate_reservation_code)

    objects = models.Manager()
    active = ActiveReservationsManager()

    def seats(self):
        return Seat.objects.filter(pk__in=self.tickets.keys()).all()

    def total_price(self):
        return reduce((lambda acc, seat: acc + int(seat.price_for_type(self.tickets[str(seat.id)]))), self.seats(), 0)

    def ticket_set(self):
        return Ticket.objects.filter(show=self.show).filter(seat_id__in=self.tickets.keys())


class Account(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"

class Ticket(models.Model):
    price = models.IntegerField()
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES, default="normal")
    show = models.ForeignKey(Show, null=False)
    seat = models.ForeignKey(Seat, null=False)
    account = models.ForeignKey(Account, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    ticket_code = models.CharField(unique=True, max_length=16, default=_generate_reservation_code)

    class Meta:
        unique_together = ('show', 'seat')

    def __repr__(self):
        return "<Ticket %s | %s | %s>" % (self.ticket_type, self.show, self.seat)

    def __str__(self):
        return f"{self.show}, {self.seat.group}, {self.seat}"

class Voucher(models.Model):
    reservation = models.ForeignKey(Reservation, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    rebate_amount = models.IntegerField(help_text="Rabatt i SEK")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


class ActivePricingModelManager(models.Manager):
    def active(self, timestamp=None):
        if not timestamp:
            timestamp = timezone.now()
        return super().get_queryset().filter(valid_from__lte=timestamp).order_by("-valid_from")


class PricingModel(models.Model):
    """
    A pricing model for a seating group.
    """

    seating_group = models.ForeignKey(SeatingGroup, null=False)
    prices = HStoreField(null=False)
    valid_from = models.DateTimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    objects = ActivePricingModelManager()

    def price_for(self, ticket_type):
        return int(self.prices[ticket_type])

    def __repr__(self):
        return "<PricingModel(id={}, prices={}, seating_group={}, valid_from={})>".format(
            self.id,
            self.prices,
            self.seating_group,
            self.valid_from
        )

    def __str__(self):
        return f"PricingModel {self.id} {self.valid_from} {self.prices} {self.seating_group}"

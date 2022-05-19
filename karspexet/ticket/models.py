from __future__ import annotations

import enum
from datetime import date
from string import ascii_uppercase, digits

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from karspexet.venue.models import Seat


class TicketType(str, enum.Enum):
    normal = "normal"
    student = "student"
    sponsor = "sponsor"

    def __str__(self) -> str:
        return self.value


TICKET_TYPES = [
    (TicketType.normal, "Fullpris"),
    (TicketType.student, "Student"),
    (TicketType.sponsor, "Sponsor"),
]


def _generate_random_code(length=12):
    return get_random_string(length=length, allowed_chars=ascii_uppercase + digits)


def _generate_voucher_code():
    return _generate_random_code(length=16)


def _next_fifteenth_september():
    # By the 15nth of September, the previous show season is usually over
    today = timezone.now().date()
    fifteenth_september_this_year = date(today.year, 9, 15)
    fifteenth_september_next_year = date(today.year + 1, 9, 15)

    if today >= fifteenth_september_this_year:
        return fifteenth_september_next_year
    else:
        return fifteenth_september_this_year


class ActiveReservationsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(session_timeout__gt=timezone.now()) | Q(finalized=True))


class Reservation(models.Model):
    show = models.ForeignKey("show.Show", null=False, on_delete=models.CASCADE)
    ticket_price = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    tickets = HStoreField()
    session_timeout = models.DateTimeField()
    finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    reservation_code = models.CharField(unique=True, max_length=16, default=_generate_random_code)

    objects = models.Manager()
    active = ActiveReservationsManager()

    def __repr__(self):
        fields = ["id", "show_id"]
        return "<%s(%s)>" % (type(self).__name__, ", ".join(f"{f}={getattr(self, f)}" for f in fields))

    def __str__(self):
        return repr(self)

    def save(self, *args, **kwargs) -> None:
        self.calculate_ticket_price_and_total()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("reservation_detail", kwargs={"reservation_code": self.reservation_code})

    def get_amount(self) -> int:
        return self.total * 100  # Price in Öre

    def is_free(self) -> bool:
        return self.get_amount() == 0

    def seat_ids(self) -> list:
        if not self.tickets:
            return []
        return list(self.tickets.keys())

    def seats(self):
        return Seat.objects.filter(pk__in=self.seat_ids()).all()

    def ticket_set(self):
        return Ticket.objects.filter(show=self.show).filter(seat_id__in=self.seat_ids())

    def num_tickets(self) -> int:
        return len(self.seat_ids())

    def apply_voucher(self, code) -> Discount:
        if Discount.objects.filter(reservation=self).exists():
            raise AlreadyDiscountedException("This reservation already has a discount: reservation_id=%d existing_discount_code=%s new_code=%s" % (
                self.id, self.discount.voucher.code, code))
        if Discount.objects.filter(Q(voucher__code=code)).exists():
            raise InvalidVoucherException("Voucher has already been used: code=%s" % code)
        voucher = Voucher.objects.get(code=code)
        amount = min(self.ticket_price, voucher.amount)
        discount = Discount.objects.create(reservation=self, voucher=voucher, amount=amount)
        self.total = self.ticket_price - amount

        return discount

    def calculate_ticket_price_and_total(self) -> None:
        self.ticket_price = sum(int(seat.price_for_type(self.tickets[str(seat.id)])) for seat in self.seats())
        try:
            self.total = self.ticket_price - self.discount.amount
        except ObjectDoesNotExist:
            self.total = self.ticket_price

    def build_tickets(self, seats: dict[str, list[Seat]]) -> None:
        tickets = {}
        for price, price_seats in seats.items():
            for seat in price_seats:
                tickets[str(seat.id)] = price

        if len(tickets) != sum(map(len, seats.values())):
            raise MultipleTicketTypeException("One seat may not have multiple ticket types")

        self.tickets = tickets


class Account(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Ticket(models.Model):
    price = models.PositiveIntegerField()
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES, default="normal")
    show = models.ForeignKey("show.Show", null=False, on_delete=models.PROTECT)
    seat = models.ForeignKey("venue.Seat", null=False, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    ticket_code = models.CharField(unique=True, max_length=16, default=_generate_random_code)
    reference = models.CharField(max_length=255, null=False, blank=True, default="")

    class Meta:
        unique_together = ("show", "seat")

    def __repr__(self):
        return "<Ticket %s | %s | %s>" % (self.ticket_type, self.show, self.seat)

    def __str__(self):
        if self.show.free_seating:
            return str(self.seat.group)
        else:
            return f"{self.show}, {self.seat.group}, {self.seat}"

    def get_reservation(self) -> Reservation | None:
        qs = Reservation.objects.filter(show=self.show, finalized=True)
        return qs.filter(tickets__keys__overlap=[self.seat_id]).first()


class VoucherQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(id__in=Discount.objects.values_list("id", flat=True))


class Voucher(models.Model):
    """
    A voucher valid for getting a discount on one single Reservation.

    Vouchers cannot be partially applied to a Reservation, so any excess value is void after use.
    """
    amount = models.PositiveIntegerField(help_text="Rabatt i SEK")
    code = models.CharField(unique=True, max_length=16, null=False, default=_generate_voucher_code)
    expiry_date = models.DateField(null=False, default=_next_fifteenth_september)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    note = models.CharField(max_length=255, null=False, default="")

    objects = VoucherQuerySet.as_manager()

    @staticmethod
    def active():
        return Voucher.objects.exclude(id__in=Discount.objects.values_list('id', flat=True))

    def __str__(self):
        return f"id={self.id} amount={self.amount} code={self.code}"


class Discount(models.Model):
    """
    A model representing a given discount on a specific reservation.

    This is a connecting model between a Voucher and a Reservation.

    A Voucher can only ever be discounted to one single Reservation, and a
    Reservation can only ever have one single Discount applied.
    """
    amount = models.PositiveIntegerField(validators=[MinValueValidator(100), MaxValueValidator(5000)], null=False)
    reservation = models.OneToOneField(Reservation, null=False, unique=True, on_delete=models.CASCADE)
    voucher = models.OneToOneField(Voucher, null=False, unique=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def unused_amount(self) -> int:
        return self.voucher.amount - self.amount


class ActivePricingModelManager(models.Manager):
    def active(self, timestamp=None):
        if not timestamp:
            timestamp = timezone.now()
        return super().get_queryset().filter(valid_from__lte=timestamp).order_by("-valid_from")


class PricingModel(models.Model):
    """
    A pricing model for a seating group.
    """

    seating_group = models.ForeignKey("venue.SeatingGroup", null=False, on_delete=models.PROTECT)
    prices = HStoreField(null=False)
    valid_from = models.DateTimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    objects = ActivePricingModelManager()

    def __repr__(self):
        return "<PricingModel(id={}, prices={}, seating_group={}, valid_from={})>".format(
            self.id,
            self.prices,
            self.seating_group,
            self.valid_from
        )

    def __str__(self):
        return f"PricingModel {self.id} {self.valid_from} {self.prices} {self.seating_group}"

    def price_for(self, ticket_type) -> int:
        return int(self.prices[ticket_type])

    def save(self, **kwargs):
        if not self.prices:
            self.prices = {}
        for type in TicketType:
            self.prices.setdefault(type, None)
        super().save(**kwargs)


class InvalidVoucherException(Exception):
    pass


class AlreadyDiscountedException(Exception):
    pass


class MultipleTicketTypeException(Exception):
    pass

from __future__ import annotations

from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import ValidationError
from django.db import models


def validate_dimensions(value):
    required = {
        "height",
        "stage_height",
        "stage_width",
        "stage_x",
        "stage_y",
        "width",
    }
    filled = set(value.keys())
    missing = required - filled
    if missing:
        raise ValidationError("Värdena %s behöver fyllas i" % ", ".join(missing))


class Venue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    map_address = models.CharField(blank=True, max_length=255)
    seat_map_dimensions = HStoreField(
        null=False, default=dict, blank=True, validators=[validate_dimensions]
    )

    def __str__(self):
        return self.name


class SeatingGroup(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.venue.name} / {self.name}"

    def active_pricing_model(self, timestamp=None):
        return (
            self.pricingmodel_set.active(timestamp)
            .filter(seating_group_id=self.id)
            .first()
        )


class SeatManager(models.Manager):
    def available_seats(self, show) -> list[Seat]:
        taken_seats = set(show.ticket_set.values_list("seat_id", flat=True))
        reserved_seats = show.reservation_set(manager="active").values_list(
            "tickets", flat=True
        )
        for tickets in reserved_seats:
            taken_seats.update(map(int, tickets.keys()))
        seats = Seat.objects.filter(group__venue=show.venue).exclude(id__in=taken_seats)
        return list(seats)


class Seat(models.Model):
    group = models.ForeignKey(SeatingGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, help_text='Till exempel "Rad 17, Stol 5011"')
    x_pos = models.IntegerField()
    y_pos = models.IntegerField()

    objects = SeatManager()

    def __str__(self):
        return self.name

    def price_for_type(self, ticket_type, timestamp=None):
        return self.group.active_pricing_model(timestamp).price_for(ticket_type)

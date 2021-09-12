from __future__ import annotations

from datetime import datetime

from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from karspexet.venue.models import Venue


class Production(models.Model):
    name = models.CharField(max_length=100)
    alt_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ShowQuerySet(models.QuerySet):
    def annotate_ticket_coverage(self) -> list[Show]:
        """
        Aggregates the ticket and seat counts for each show in the query
        """
        shows = self.prefetch_related("production").annotate(ticket_count=Count("ticket"))

        venue_ids = {show.venue_id for show in shows}
        venues: dict[int, Venue] = (
            Venue.objects.filter(id__in=venue_ids)
            .annotate(seat_count=Count("seatinggroup__seat"))
            .in_bulk()
        )

        for show in shows:
            venue = venues[show.venue_id]
            show.venue = venue
            show.sales_percentage = 100 * ((show.ticket_count / venue.seat_count) if venue.seat_count else 0)

        return shows


class Show(models.Model):
    production = models.ForeignKey(Production, on_delete=models.PROTECT)
    date = models.DateTimeField()
    venue = models.ForeignKey("venue.Venue", on_delete=models.PROTECT)
    visible = models.BooleanField(default=True)
    slug = models.CharField(max_length=20, unique=True, default=get_random_string)
    short_description = models.CharField(null=False, blank=True, default="", max_length=255)
    free_seating = models.BooleanField(default=False, null=False, help_text="Fri placering")

    objects = ShowQuerySet.as_manager()

    class Meta:
        ordering = ("date",)

    def __str__(self) -> str:
        short = f"({self.short_description}) " if self.short_description else ""
        return f"{self.production.name} {short}{self.date_string()}"

    def get_absolute_url(self) -> str:
        return reverse("select_seats", args=[self.id])

    @staticmethod
    def upcoming():
        return Show.objects.filter(date__gte=timezone.make_aware(datetime.today()))

    def date_string(self):
        return timezone.localtime(self.date).strftime("%Y-%m-%d %H:%M")

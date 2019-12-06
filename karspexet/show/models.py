from django.utils.crypto import get_random_string

from django.db import models
from datetime import datetime
from django.utils import timezone


class Production(models.Model):
    name = models.CharField(max_length=100)
    alt_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Show(models.Model):
    production = models.ForeignKey(Production, on_delete=models.PROTECT)
    date = models.DateTimeField()
    venue = models.ForeignKey('venue.Venue', on_delete=models.PROTECT)
    visible = models.BooleanField(default=True)
    slug = models.CharField(max_length=20, unique=True, default=get_random_string)
    short_description = models.CharField(null=False, blank=True, default="", max_length=255)
    free_seating = models.BooleanField(default=False, null=False, help_text="Fri placering")

    @staticmethod
    def upcoming():
        return Show.objects.filter(date__gte=timezone.make_aware(datetime.today()))

    @staticmethod
    def ticket_coverage(show=None):
        if show is None:
            show_ids = Show.objects.order_by("-id").values_list('id', flat=True)
        else:
            show_ids = [show.id]

        coverage_data = []

        for show_id in show_ids:
            coverage_data.extend(Show.objects.raw(f"""
            SELECT show.id,
                show.production_id,
                show.venue_id,
                show.short_description,
                venue.name as venue_name,
                production.name as production_name,
                show.date,
                COUNT(DISTINCT(ticket.id)) AS ticket_count,
                COUNT(DISTINCT(seat.id)) AS seat_count,
                100 * (COUNT(DISTINCT(ticket.id))::float / COUNT(DISTINCT(seat.id))) AS sales_percentage
            FROM show_show show
                LEFT JOIN venue_venue venue ON show.venue_id = venue.id
                LEFT JOIN venue_seatinggroup sg ON sg.venue_id = venue.id
                LEFT JOIN venue_seat seat ON sg.id = seat.group_id
                LEFT JOIN show_production production ON show.production_id = production.id
                LEFT OUTER JOIN ticket_ticket ticket ON ticket.show_id = show.id
              WHERE show.id = {show_id}
            GROUP BY show.id, venue.id, production.id
            """))

        return coverage_data

    def date_string(self):
        return timezone.localtime(self.date).strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        short = f"({self.short_description}) " if self.short_description else ""
        return f"{self.production.name} {short}{self.date_string()}"

    class Meta:
        ordering = ('date',)

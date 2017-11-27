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

    @staticmethod
    def upcoming():
        return Show.objects.filter(date__gte=timezone.make_aware(datetime.today()))

    @staticmethod
    def ticket_coverage(show=None):
        return Show.objects.raw(f"""
            SELECT show.id,
                show.production_id,
                show.venue_id,
                venue.name as venue_name,
                production.name as production_name,
                show.date,
                COUNT(DISTINCT(ticket.id)) AS ticket_count,
                COUNT(DISTINCT(seat.id)) AS seat_count,
                100 * (COUNT(DISTINCT(ticket.id))::float / COUNT(DISTINCT(seat.id))) AS sales_percentage
            FROM show_show show
                LEFT OUTER JOIN ticket_ticket ticket ON ticket.show_id = show.id
                LEFT JOIN venue_venue venue ON show.venue_id = venue.id
                LEFT JOIN venue_seatinggroup sg ON sg.venue_id = venue.id
                LEFT JOIN venue_seat seat ON sg.id = seat.group_id
                LEFT JOIN show_production production ON show.production_id = production.id
            {f'WHERE show.id = {show.id}' if show else ''}
            GROUP BY show.id, venue.name, production.name
            ORDER BY show.date desc
            """)

    def date_string(self):
        return self.date.strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        return self.production.name + " " + self.date_string()

    class Meta:
        ordering = ('date',)

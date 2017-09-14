from django.db import models
import datetime


class Production(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Show(models.Model):
    production = models.ForeignKey(Production, on_delete=models.PROTECT)
    date = models.DateTimeField()
    venue = models.ForeignKey('venue.Venue', on_delete=models.PROTECT)

    @staticmethod
    def upcoming():
        return Show.objects.filter(date__gte=datetime.date.today())

    @staticmethod
    def ticket_coverage():
        return Show.objects.raw("""
            select show.id,
                show.production_id,
                show.venue_id,
                venue.name as venue_name,
                production.name as production_name,
                show.date,
                count(distinct(ticket.id)) as ticket_count,
                count(distinct(seat.id)) as seat_count,
                100 * (count(distinct(ticket.id))::float / count(distinct(seat.id))) as sales_percentage
            from show_show show
                left outer join ticket_ticket ticket on ticket.show_id = show.id
                left join venue_venue venue on show.venue_id = venue.id
                left join venue_seatinggroup sg on sg.venue_id = venue.id
                left join venue_seat seat on sg.id = seat.group_id
                left join show_production production on show.production_id = production.id
            group by show.id, venue.name, production.name
            order by show.date desc
            """)

    def date_string(self):
        return self.date.strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        return self.production.name + " " + self.date_string()

    class Meta:
        ordering = ('date',)

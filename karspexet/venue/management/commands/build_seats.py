import csv

from django.core.management.base import BaseCommand

from karspexet.venue.models import Seat, SeatingGroup, Venue


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("venue-id", type=int)
        parser.add_argument("file")
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        venue = Venue.objects.get(pk=options["venue-id"])

        if options["clear"]:
            Seat.objects.filter(group__venue=venue).delete()
            SeatingGroup.objects.filter(venue=venue).delete()

        groupings = {group.name: group for group in SeatingGroup.objects.filter(venue=venue)}

        count = 0
        for group_name, x_pos, y_pos, seat_name in self._read_file(options["file"]):
            group = groupings.get(group_name, None)
            if group is None:
                group = SeatingGroup.objects.create(
                    name=group_name,
                    venue=venue
                )
                groupings[group_name] = group

            _, created = Seat.objects.get_or_create(
                group=group,
                name=seat_name,
                x_pos=x_pos,
                y_pos=y_pos,
            )
            if created:
                count += created

        total = Seat.objects.filter(group__venue=venue).count()
        self.stdout.write("Created %s new Seats for %s (now has %s)" % (count, venue, total))

    @staticmethod
    def _read_file(filename):
        with open(filename) as csv_file:
            reader = csv.reader(csv_file)
            return list(reader)

import csv

from django.core.management.base import BaseCommand

from karspexet.venue.models import Seat, SeatingGroup, Venue


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("venue-id", type=int)
        parser.add_argument("file")

    def handle(self, *args, **options):
        venue = Venue.objects.get(pk=options["venue-id"])

        with open(options["file"]) as csv_file:
            reader = csv.reader(csv_file, delimiter="\t")
            groupings = {}

            for group_name, seat_name, x_pos, y_pos in reader:
                group = groupings.get(group_name, None)
                if group is not None:
                    group = SeatingGroup.objects.create(
                        name=group_name,
                        venue=venue
                    )
                    groupings[group_name] = group

                Seat.objects.create(
                    group=group,
                    name=seat_name,
                    x_pos=x_pos,
                    y_pos=y_pos,
                )

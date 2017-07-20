from django.db import models
from django.utils import timezone


class Venue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SeatingGroup(models.Model):
    venue = models.ForeignKey(Venue)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def active_pricing_model(self, timestamp=None):
        return self.pricingmodel_set.active(timestamp).filter(seating_group_id=self.id).first()


class Seat(models.Model):
    group = models.ForeignKey(SeatingGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, help_text='Till exempel "Rad 17, Stol 5011"')
    x_pos = models.IntegerField()
    y_pos = models.IntegerField()

    def __str__(self):
        return self.name

    def price_for_type(self, ticket_type, timestamp=None):
        return self.group.active_pricing_model(timestamp).price_for(ticket_type)

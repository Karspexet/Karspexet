from django.db import models


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


class Seat(models.Model):
    group = models.ForeignKey(SeatingGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, help_text='Till exempel "Rad 17, Stol 5011"')

    def __str__(self):
        return self.name

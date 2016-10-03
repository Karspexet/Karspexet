from django.db import models


class Production(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Show(models.Model):
    production = models.ForeignKey(Production, on_delete=models.PROTECT)
    date = models.DateField()
    venue = models.ForeignKey('venue.Venue', on_delete=models.PROTECT)

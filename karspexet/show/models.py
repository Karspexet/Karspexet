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

    def date_string(self):
        return self.date.strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        return self.production.name + " " + self.date_string()

    class Meta:
        ordering = ('date',)

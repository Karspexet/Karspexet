from django.db import models

class Show(models.Model):
    at = models.DateTimeField("date it's shown")
    name = models.CharField(max_length=200)

class Ticket(models.Model):
    position = models.CharField(max_length=200)
    price = models.PositiveSmallIntegerField()
    show = models.ForeignKey(Show)


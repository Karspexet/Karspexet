from factory.django import DjangoModelFactory
from django.contrib.auth.models import User


class CreateVenue(DjangoModelFactory):
    class Meta:
        model = 'venue.venue'


class CreateSeatingGroup(DjangoModelFactory):
    class Meta:
        model = 'venue.seatinggroup'


class CreateSeat(DjangoModelFactory):
    x_pos = 0
    y_pos = 0

    class Meta:
        model = 'venue.seat'


class CreateShow(DjangoModelFactory):
    class Meta:
        model = 'show.show'


class CreateProduction(DjangoModelFactory):
    class Meta:
        model = 'show.production'


class CreateReservation(DjangoModelFactory):
    class Meta:
        model = 'ticket.reservation'


class CreateAccount(DjangoModelFactory):
    class Meta:
        model = 'ticket.account'


class CreateTicket(DjangoModelFactory):
    class Meta:
        model = 'ticket.ticket'


class CreateVoucher(DjangoModelFactory):
    class Meta:
        model = 'ticket.voucher'


class CreatePricingModel(DjangoModelFactory):
    class Meta:
        model = 'ticket.pricingmodel'


def CreateStaffUser(username, password):
    user = User.objects.create_user(username, email="ture@example.com")
    user.set_password(password)
    user.is_staff = True
    user.save()
    return user

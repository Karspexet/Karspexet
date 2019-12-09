import factory
from django.contrib.auth.models import User
from django.utils import timezone
from factory.django import DjangoModelFactory


class CreateStaffUser(DjangoModelFactory):
    email = "ture@example.com"
    is_staff = True

    class Meta:
        model = User

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted)
        self.save()


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
    date = timezone.now()
    production = factory.SubFactory('factories.factories.CreateProduction')
    venue = factory.SubFactory('factories.factories.CreateVenue')

    class Meta:
        model = 'show.show'


class CreateProduction(DjangoModelFactory):
    class Meta:
        model = 'show.production'


class CreateReservation(DjangoModelFactory):
    class Meta:
        model = 'ticket.Reservation'
    session_timeout = timezone.now()


class CreateAccount(DjangoModelFactory):
    name = "Bonnie"
    email = "bonnie@example.com"

    class Meta:
        model = 'ticket.account'


class CreateTicket(DjangoModelFactory):
    price = 200
    account = factory.SubFactory('factories.factories.CreateAccount')

    class Meta:
        model = 'ticket.ticket'


class CreateVoucher(DjangoModelFactory):
    class Meta:
        model = 'ticket.voucher'

    amount = 100
    created_by = factory.SubFactory(CreateStaffUser)


class CreatePricingModel(DjangoModelFactory):
    class Meta:
        model = 'ticket.pricingmodel'

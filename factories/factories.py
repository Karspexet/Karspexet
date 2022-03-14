import factory
from django.contrib.auth.models import User
from django.utils import timezone
from factory import LazyAttribute, post_generation
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
        model = "venue.Venue"

    @post_generation
    def num_seats(self, create, num_seats, **kwargs):
        if not num_seats:
            return
        group = CreateSeatingGroup(venue=self)
        CreatePricingModel(seating_group=group, prices={"student": 200, "normal": 250})
        for i in range(num_seats):
            CreateSeat(group=group)


class CreateSeatingGroup(DjangoModelFactory):
    class Meta:
        model = "venue.seatinggroup"


class CreateSeat(DjangoModelFactory):
    x_pos = 0
    y_pos = 0

    class Meta:
        model = "venue.Seat"


class CreateShow(DjangoModelFactory):
    date = timezone.now()
    production = factory.SubFactory("factories.factories.CreateProduction")
    venue = factory.SubFactory("factories.factories.CreateVenue")

    class Meta:
        model = "show.Show"


class CreateProduction(DjangoModelFactory):
    class Meta:
        model = "show.Production"


class CreateReservation(DjangoModelFactory):
    class Meta:
        model = "ticket.Reservation"

    show = factory.SubFactory("factories.factories.CreateShow")
    session_timeout = timezone.now()


class CreateAccount(DjangoModelFactory):
    name = "Bonnie"
    email = "bonnie@example.com"

    class Meta:
        model = "ticket.Account"


class CreateTicket(DjangoModelFactory):
    price = 200
    account = factory.SubFactory("factories.factories.CreateAccount")

    class Meta:
        model = "ticket.Ticket"


class CreateVoucher(DjangoModelFactory):
    class Meta:
        model = "ticket.Voucher"

    amount = 100
    created_by = factory.SubFactory(CreateStaffUser)


class CreateDiscount(DjangoModelFactory):
    class Meta:
        model = "ticket.Discount"

    amount = 100
    voucher = factory.SubFactory(CreateVoucher)


class CreatePricingModel(DjangoModelFactory):
    class Meta:
        model = "ticket.PricingModel"

    valid_from = LazyAttribute(lambda a: timezone.now())

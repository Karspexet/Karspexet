import factory
from django.contrib.auth.models import User
from django.utils import timezone
from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory


class CreateStaffUser(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    is_staff = True
    email = "ture@example.com"
    username = "ture@example.com"

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
        model = "venue.SeatingGroup"

    venue = factory.SubFactory("factories.factories.CreateVenue")


class CreateSeat(DjangoModelFactory):
    class Meta:
        model = "venue.Seat"

    x_pos = 0
    y_pos = 0
    group = factory.SubFactory("factories.factories.CreateSeatingGroup")


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


class CreateReservationWithTicket(CreateReservation):
    @factory.lazy_attribute
    def tickets(self):
        group = CreateSeatingGroup(venue=self.show.venue)
        CreatePricingModel(seating_group=group, prices={"student": 200, "normal": 250})
        seat = CreateSeat(group=group)
        return {str(seat.id): "normal"}

    show = factory.SubFactory("factories.factories.CreateShow")
    session_timeout = timezone.now()


class CreateAccount(DjangoModelFactory):
    name = "Bonnie"
    email = "bonnie@example.com"

    class Meta:
        model = "ticket.Account"


class CreateTicket(DjangoModelFactory):
    class Meta:
        model = "ticket.Ticket"

    price = 200
    account = factory.SubFactory("factories.factories.CreateAccount")
    show = factory.SubFactory("factories.factories.CreateShow")
    seat = factory.SubFactory("factories.factories.CreateSeat")


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

    seating_group = factory.SubFactory("factories.factories.CreateSeatingGroup")
    valid_from = LazyAttribute(lambda a: timezone.now())

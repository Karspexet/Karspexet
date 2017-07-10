from factory.django import DjangoModelFactory

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

class CreateReservation(DjangoModelFactory):
    class Meta:
        model = 'ticket.account'

class CreateReservation(DjangoModelFactory):
    class Meta:
        model = 'ticket.ticket'

class CreateReservation(DjangoModelFactory):
    class Meta:
        model = 'ticket.voucher'

class CreatePricingModel(DjangoModelFactory):
    class Meta:
        model = 'ticket.pricingmodel'

from factory.django import DjangoModelFactory

class CreateVenue(DjangoModelFactory):
    class Meta:
        model = 'venue.venue'

class CreateSeatingGroup(DjangoModelFactory):
    class Meta:
        model = 'venue.seatinggroup'

class CreateSeat(DjangoModelFactory):
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

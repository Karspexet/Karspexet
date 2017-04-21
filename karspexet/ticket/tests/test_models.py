from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase

from factories import factories as f

from karspexet.ticket.models import Reservation

class TestReservation(TestCase):
    def setUp(self):
        venue = f.CreateVenue()
        group = f.CreateSeatingGroup(venue=venue)
        self.seat1 = f.CreateSeat(group=group)
        self.seat2 = f.CreateSeat(group=group)

        production = f.CreateProduction()
        self.show = f.CreateShow(production=production, venue=venue, date=datetime.now())

    def test_reservation_is_active_if_session_timer_has_not_passed(self):
        timestamp = datetime.now() + relativedelta(minutes=10)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )

        self.assertTrue(reservation in Reservation.active.all())


    def test_finalized_reservation_is_active(self):
        timestamp = datetime.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            finalized=True,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )

        self.assertTrue(reservation in Reservation.active.all())

    def test_timed_out_reservation_is_not_active(self):
        timestamp = datetime.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )


        self.assertTrue(reservation in Reservation.objects.all())
        self.assertFalse(reservation in Reservation.active.all())

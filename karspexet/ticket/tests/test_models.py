from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from factories import factories as f

from karspexet.ticket.models import Reservation, PricingModel

class TestReservation(TestCase):
    def setUp(self):
        venue = f.CreateVenue()
        group = f.CreateSeatingGroup(venue=venue)
        pricing = f.CreatePricingModel(
            seating_group=group,
            prices={'student': 200, 'normal': 250},
            valid_from=timezone.now()
        )
        self.seat1 = f.CreateSeat(group=group)
        self.seat2 = f.CreateSeat(group=group)

        production = f.CreateProduction()
        self.show = f.CreateShow(production=production, venue=venue, date=timezone.now())

    def test_reservation_is_active_if_session_timer_has_not_passed(self):
        timestamp = timezone.now() + relativedelta(minutes=10)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )

        assert reservation in Reservation.active.all()

    def test_finalized_reservation_is_active(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            finalized=True,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )

        assert reservation in Reservation.active.all()

    def test_timed_out_reservation_is_not_active(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={},
            total=200,
        )

        assert reservation in Reservation.objects.all()
        assert reservation not in Reservation.active.all()


    def test_total_price(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            total=0,
            session_timeout=timestamp,
            tickets={
                self.seat1.id: 'student',
                self.seat2.id: 'normal',
            },
        )
        reservation = Reservation.objects.get(pk=reservation.id)

        assert reservation.total_price() == 450

class TestPricingModel(TestCase):
    def setUp(self):
        venue = f.CreateVenue()
        self.group = f.CreateSeatingGroup(venue=venue)

    def test_price_for(self):
        pricing = PricingModel.objects.create(
            seating_group=self.group,
            valid_from=timezone.now(),
            prices={
                'student': 200,
                'normal': 250,
            },
        )

        assert pricing.price_for('student') == 200
        assert pricing.price_for('normal') == 250

    def test_price_for_at_past_date(self):
        old_pricing = PricingModel.objects.create(
            seating_group=self.group,
            valid_from=timezone.now() - relativedelta(days=2),
            prices={
                'student': 150,
                'normal': 200,
            },
        )
        new_pricing = PricingModel.objects.create(
            seating_group=self.group,
            valid_from=timezone.now(),
            prices={
                'student': 200,
                'normal': 250,
            },
        )
        seat = f.CreateSeat(group=self.group)
        one_day_ago = timezone.now() - relativedelta(days=1)

        assert seat.price_for_type('student') == 200
        assert seat.price_for_type('student', one_day_ago) == 150

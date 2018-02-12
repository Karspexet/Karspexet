import pytest

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from factories import factories as f

from karspexet.ticket.models import PricingModel, Reservation, Ticket
from django.core.exceptions import ValidationError

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

    def test_reservations_have_auto_generated_reservation_code(self):
        reservation_1 = Reservation()
        reservation_2 = Reservation()

        assert len(reservation_1.reservation_code) == 12
        assert reservation_1.reservation_code is not reservation_2.reservation_code


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

class TestTicket(TestCase):
    def setUp(self):
        production = f.CreateProduction()
        venue = f.CreateVenue()
        group = f.CreateSeatingGroup(venue=venue)
        self.seat = f.CreateSeat(group=group)
        self.show = f.CreateShow(venue=venue, production=production, date=timezone.now())
        self.pricing = f.CreatePricingModel(
            seating_group=group,
            prices={'student': 200, 'normal': 250},
            valid_from=timezone.now()
        )

    def test_ticket_must_be_unique_per_show(self):
        old_ticket = f.CreateTicket(show=self.show, seat=self.seat, price=200, account=f.CreateAccount())

        duplicate_ticket = Ticket(show=self.show, seat=self.seat, price=200, account=f.CreateAccount())

        with pytest.raises(ValidationError) as error:
            duplicate_ticket.full_clean()


class TestDiscount:
    def discount_must_have_a_unique_voucher_reservation_combo():
        pass

from datetime import date, datetime
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from factories import factories as f
from karspexet.ticket.models import (
    AlreadyDiscountedException,
    InvalidVoucherException,
    PricingModel,
    Reservation,
    Ticket,
    Voucher,
)
from karspexet.venue.models import Seat


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
        )

        assert reservation in Reservation.active.all()

    def test_finalized_reservation_is_active(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            finalized=True,
            session_timeout=timestamp,
            tickets={},
        )

        assert reservation in Reservation.active.all()

    def test_timed_out_reservation_is_not_active(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={},
        )

        assert reservation in Reservation.objects.all()
        assert reservation not in Reservation.active.all()

    def test_ticket_price_and_total(self):
        timestamp = timezone.now() - relativedelta(days=1)
        reservation = Reservation.objects.create(
            show=self.show,
            session_timeout=timestamp,
            tickets={
                str(self.seat1.id): 'student',
                str(self.seat2.id): 'normal',
            },
        )

        assert reservation.total == 450

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


@pytest.mark.django_db
class TestDiscount:
    def test_discount_lowers_the_total_of_a_reservation(self, show, user):
        seat = Seat.objects.first()
        tickets = {str(seat.id): 'normal'}
        reservation = f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)
        voucher = Voucher.objects.create(amount=100, created_by=user)
        discount = reservation.apply_voucher(voucher.code)

        assert discount.amount == 100
        assert reservation.total == reservation.ticket_price - 100

    def test_discount_can_result_in_free_tickets(self, show, user):
        seat = Seat.objects.first()
        tickets = {str(seat.id): 'normal'}
        reservation = f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)
        voucher = Voucher.objects.create(amount=reservation.ticket_price, created_by=user)
        discount = reservation.apply_voucher(voucher.code)

        assert discount.amount == reservation.ticket_price
        assert reservation.total == 0

    def test_excess_voucher_amount_is_void(self, show, user):
        seat = Seat.objects.first()
        tickets = {str(seat.id): 'normal'}
        reservation = f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)
        voucher = Voucher.objects.create(amount=300, created_by=user)
        discount = reservation.apply_voucher(voucher.code)

        assert discount.amount == reservation.ticket_price
        assert reservation.total == 0

    def test_a_voucher_cannot_be_reused(self, show, user):
        seat = Seat.objects.all()[0]
        seat2 = Seat.objects.all()[1]
        reservation = f.CreateReservation(
            tickets={str(seat.id): 'normal'},
            session_timeout=timezone.now(),
            show=show
        )
        reservation2 = f.CreateReservation(
            tickets={str(seat.id): 'normal'},
            session_timeout=timezone.now(),
            show=show
        )

        voucher = Voucher.objects.create(amount=300, created_by=user)

        discount = reservation.apply_voucher(voucher.code)
        with pytest.raises(InvalidVoucherException):
            reservation2.apply_voucher(voucher.code)

        assert discount.amount == reservation.ticket_price
        assert reservation.total == 0
        assert reservation2.total == reservation2.ticket_price

    def test_a_voucher_cannot_have_multiple_discounts(self, show, user):
        seat = Seat.objects.first()
        tickets = {str(seat.id): 'normal'}
        reservation = f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)
        voucher = Voucher.objects.create(amount=100, created_by=user)
        voucher2 = Voucher.objects.create(amount=100, created_by=user)
        discount = reservation.apply_voucher(voucher.code)

        with pytest.raises(AlreadyDiscountedException):
            reservation.apply_voucher(voucher2.code)

        assert discount.amount == 100
        assert reservation.total == 150

    def test_a_voucher_expires_nextcoming_fifteenth_of_september(self):
        user = f.CreateStaffUser(username="test", password="test")
        this_year = date.today().year
        next_year = this_year + 1
        start_of_year = datetime(this_year, 1, 2)
        end_of_year = datetime(this_year, 12, 30)
        with patch("karspexet.ticket.models.timezone.now", return_value=start_of_year):
            voucher = Voucher(amount=100, created_by=user)
            assert voucher.expiry_date == date(this_year, 9, 15)

        with patch("karspexet.ticket.models.timezone.now", return_value=end_of_year):
            voucher = Voucher(amount=100, created_by=user)
            assert voucher.expiry_date == date(next_year, 9, 15)

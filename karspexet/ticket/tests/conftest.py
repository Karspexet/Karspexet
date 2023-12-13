import pytest
from django.utils import timezone

from factories import factories as f


@pytest.fixture
def show():
    venue = f.CreateVenue()
    group = f.CreateSeatingGroup(venue=venue)
    f.CreatePricingModel(
        seating_group=group,
        prices={"student": 200, "normal": 250},
        valid_from=timezone.now(),
    )
    f.CreateSeat(group=group)
    f.CreateSeat(group=group)

    production = f.CreateProduction()
    return f.CreateShow(production=production, venue=venue, date=timezone.now())


@pytest.fixture
def user():
    return f.CreateStaffUser(username="test", password="test")

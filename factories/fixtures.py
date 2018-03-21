import pytest
from factories import factories as f
from django.utils import timezone

@pytest.fixture
def show():
    venue = f.CreateVenue()
    group = f.CreateSeatingGroup(venue=venue)
    pricing = f.CreatePricingModel(
        seating_group=group,
        prices={'student': 200, 'normal': 250},
        valid_from=timezone.now()
    )
    f.CreateSeat(group=group)
    f.CreateSeat(group=group)

    production = f.CreateProduction()
    return f.CreateShow(production=production, venue=venue, date=timezone.now())


@pytest.fixture
def user():
    return f.CreateStaffUser(username="test", password="test")



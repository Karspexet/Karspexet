import pytest

from tickets.models import Show, Ticket
from django.utils import timezone

@pytest.fixture
def valid_show():
    return Show(at=timezone.now(), name="Bonnie & Clyde")

@pytest.fixture
def saved_show(valid_show):
    valid_show.save()
    return valid_show

@pytest.fixture
def valid_ticket(valid_show):
    valid_show.save()
    return Ticket(position="34", price=140, show=valid_show)

import pytest

from django.utils import timezone
from tickets.models import Show, Ticket

def test_can_create_tickets():
    show = Show(at=timezone.now(), name="Bonnie & Clyde")
    ticket = Ticket(position="34", price=140, show=show)

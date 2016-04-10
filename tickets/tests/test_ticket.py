import pytest

from django.core.exceptions import ValidationError
from tickets.models import Ticket

def test_validation():
    ticket = Ticket()

    with pytest.raises(ValidationError) as error:
        ticket.full_clean()

    assert 'price' in error.value.message_dict
    assert 'position' in error.value.message_dict
    assert 'show' in error.value.message_dict

@pytest.mark.django_db
def test_can_create_tickets(saved_show):
    ticket = Ticket(position="34", price=140, show=saved_show)

    ticket.full_clean()
    ticket.save()

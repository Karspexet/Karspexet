import pytest

from django.core.exceptions import ValidationError
from tickets.models import Show

def test_validation():
    show = Show()

    with pytest.raises(ValidationError) as error:
        show.full_clean()

    assert 'name' in error.value.message_dict
    assert 'at' in error.value.message_dict

@pytest.mark.django_db
def test_can_create_show(valid_show):

    valid_show.full_clean()
    valid_show.save()

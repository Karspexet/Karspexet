import logging
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

logger = logging.getLogger(__file__)


def send_ticket_email_to_customer(reservation, email, name=None):
    '''Send an email to the customer with a link to their tickets

    If the supplied email is empty, this will silently fail. The reason for this is that this is used in the payment
    flow, and if we raise an error here, it will crash the payment transaction, and at that point we have likely
    charged someone's card without giving them tickets.

    Therefore the trade-off is made that if the customer fails to provide a valid email address, they will not receive
    an email. They will however, have another chance to send the reservation information via email at the
    reservation-detail page.
    '''
    if not email:
        return

    if not name:
        name = email

    to_address = f'{name} <{email}>'
    subject = 'Dina biljetter till Kårspexet'
    site = Site.objects.get_current()
    reservation_url = f'https://{site.domain}{reservation.get_absolute_url()}'
    body = render_to_string('reservation_email.txt', {
        'reservation': reservation,
        'url': reservation_url,
    })

    send_mail(
        subject,
        body,
        settings.TICKET_EMAIL_FROM_ADDRESS,
        [to_address],
        fail_silently=False,
    )

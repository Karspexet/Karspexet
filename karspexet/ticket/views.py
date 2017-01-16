from django.shortcuts import render

from karspexet.show.models import Show
from karspexet.ticket.forms import TicketTypeForm, SeatingGroupFormSet


def home(request):
    upcoming_shows = Show.upcoming()

    return render(request, "home.html", {
        'upcoming_shows': upcoming_shows
    })

def select_seats(request, show_id):
    show = Show.objects.get(id=show_id)
    forms = [SeatingGroupFormSet(seating_group) for seating_group in show.venue.seatinggroup_set.all()]

    return render(request, "select_seats.html", {
        'show': show,
        'venue': show.venue,
        'forms': forms,
    })

    # return render(request, 'enter_contact_details.html', {})

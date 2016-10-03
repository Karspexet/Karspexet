from django.shortcuts import get_object_or_404, render

from karspexet.venue.models import Venue


def venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    return render(request, "venue.html", {
        "venue": venue,
    })

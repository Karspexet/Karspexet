from __future__ import annotations

import logging

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from karspexet.venue.models import Seat, SeatingGroup, Venue

logger = logging.getLogger(__name__)


class AddSeatsForm(forms.Form):
    num_seats = forms.IntegerField(min_value=1)
    group = forms.IntegerField(widget=forms.HiddenInput)


@staff_member_required
def manage_seats(request: HttpRequest, venue_id: int) -> HttpResponse:
    """
    Backoffice view to easily add Seats to a Venue
    """
    venue: Venue = Venue.objects.filter(id=venue_id).first()
    if not venue:
        raise Http404

    group_qs = SeatingGroup.objects.filter(venue=venue).annotate(num_seats=Count("seat"))
    groups: list[SeatingGroup] = list(group_qs)

    if request.method == "POST":
        form = AddSeatsForm(data=request.POST)
        form.is_valid()
        if form.is_valid():
            group = form.cleaned_data["group"]
            num_seats = form.cleaned_data["num_seats"]
            for i in range(num_seats):
                number = Seat.objects.filter(group__venue=venue).count() + 1
                seat = Seat.objects.create(
                    group_id=group,
                    name="Plats %s" % number,
                    x_pos=0,
                    y_pos=0,
                )
                logger.info("Created %s - %s", venue.name, seat.name)
            messages.success(request, f"Skapade {num_seats} extra sittplatser")
        return redirect("manage_seats", venue_id=venue.id)

    return render(request, "venue/manage_seats.html", {
        "venue": venue,
        "groups": groups,
    })

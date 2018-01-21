from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse

from karspexet.show.models import Show
from karspexet.ticket.models import Ticket
# Create your views here.

@staff_member_required
def overview(request):
    shows = Show.ticket_coverage()
    return TemplateResponse(request, "economy/overview.html", context={
        'shows': shows,
        'user': request.user,
    })

@staff_member_required
def show_detail(request, show_id):
    show = Show.objects.get(pk=show_id)
    tickets = show.ticket_set.select_related('seat', 'account').all()
    taken_seats = Ticket.objects.filter(show=show).values_list('seat_id', flat=True)
    [coverage] = Show.ticket_coverage(show)

    return TemplateResponse(request, "economy/show_detail.html", context={
        "show": show,
        "taken_seats": taken_seats,
        "tickets": tickets,
        "coverage": coverage,
        "user": request.user,
    })

from collections import defaultdict

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from karspexet.show.models import Show
from karspexet.ticket.models import Discount, Ticket, Voucher

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
    tickets = show.ticket_set.select_related('seat', 'account')
    taken_seats = Ticket.objects.filter(show=show).values_list('seat_id', flat=True)
    ticket_counts: dict[str, int] = defaultdict(int)
    for t in tickets:
        ticket_counts[t.ticket_type] += 1
    [coverage] = Show.ticket_coverage(show)

    return TemplateResponse(request, "economy/show_detail.html", context={
        "show": show,
        "taken_seats": taken_seats,
        "tickets": tickets,
        "ticket_counts": ticket_counts,
        "coverage": coverage,
        "user": request.user,
    })


@staff_member_required
def vouchers(request):
    vouchers = Voucher.active()

    return TemplateResponse(request, "economy/vouchers.html", context={
        "vouchers": vouchers
    })


@staff_member_required
def discounts(request):
    discounts = Discount.objects.select_related("reservation", "voucher").all()

    return TemplateResponse(request, "economy/discounts.html", context={
        "discounts": discounts
    })


@staff_member_required
def create_voucher(request):
    if request.method == "POST":
        Voucher.objects.create(created_by=request.user, amount=request.POST["amount"], note=request.POST["note"])

        return redirect("economy_vouchers")

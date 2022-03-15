from collections import defaultdict

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from karspexet.economy.forms import VoucherForm
from karspexet.show.models import Show
from karspexet.ticket.models import Discount, Ticket, Voucher


@staff_member_required
def overview(request):
    shows = Show.objects.order_by("-date").annotate_ticket_coverage()
    return TemplateResponse(
        request,
        "economy/overview.html",
        context={
            "shows": shows,
            "user": request.user,
        },
    )


@staff_member_required
def show_detail(request, show_id):
    shows = Show.objects.filter(id=show_id).annotate_ticket_coverage()
    show = shows[0]

    tickets = show.ticket_set.select_related("seat", "account")
    taken_seats = Ticket.objects.filter(show=show).values_list("seat_id", flat=True)
    ticket_counts: dict[str, int] = defaultdict(int)
    for t in tickets:
        ticket_counts[t.ticket_type] += 1

    return TemplateResponse(
        request,
        "economy/show_detail.html",
        context={
            "show": show,
            "taken_seats": taken_seats,
            "tickets": tickets,
            "ticket_counts": ticket_counts,
            "user": request.user,
        },
    )


@staff_member_required
def discounts(request):
    discounts = Discount.objects.select_related("reservation", "voucher").all()

    return TemplateResponse(
        request,
        "economy/discounts.html",
        context={
            "discounts": discounts,
        },
    )


@staff_member_required
def vouchers(request):
    vouchers = Voucher.objects.active().order_by("-created_at")

    form = VoucherForm(data=request.POST or None, created_by=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("economy_vouchers")

    return TemplateResponse(
        request,
        "economy/vouchers.html",
        context={
            "form": form,
            "vouchers": vouchers,
        },
    )

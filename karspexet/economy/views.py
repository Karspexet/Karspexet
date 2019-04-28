from urllib.parse import urlencode

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.template.defaulttags import register
from django.template.response import TemplateResponse

from karspexet.show.models import Show
from karspexet.ticket.models import Ticket, Voucher, Discount
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
    order_by = request.GET.get('order_by', 'created_at')
    tickets = show.ticket_set.select_related('seat', 'account').all().order_by(order_by)
    taken_seats = Ticket.objects.filter(show=show).values_list('seat_id', flat=True)
    number_students = tickets.filter(ticket_type="student").count()
    number_normal = tickets.filter(ticket_type="normal").count()
    [coverage] = Show.ticket_coverage(show)

    return TemplateResponse(request, "economy/show_detail.html", context={
        "show": show,
        "taken_seats": taken_seats,
        "tickets": tickets,
        "number_students": number_students,
        "number_normal": number_normal,
        "coverage": coverage,
        "user": request.user,
    })


@register.simple_tag
def order_by(request, value, direction=''):
    dict_ = request.GET.copy()
    field = 'order_by'
    if field in dict_.keys():
        if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
            dict_[field] = value
        elif dict_[field].lstrip('-') == value:
            dict_[field] = "-" + value
        else:
            dict_[field] = direction + value
    else:
        dict_[field] = direction + value
    return urlencode(dict(dict_.items()))


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

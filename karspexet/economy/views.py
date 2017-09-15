from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse

from karspexet.show.models import Show
# Create your views here.

@staff_member_required
def overview(request):
    shows = Show.ticket_coverage()
    return TemplateResponse(request, "economy/overview.html", context={
        'shows': shows,
        'user': request.user,
    })

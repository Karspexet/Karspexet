from django.shortcuts import reverse


def admin_change_url(obj) -> str:
    return reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=(obj.pk,))

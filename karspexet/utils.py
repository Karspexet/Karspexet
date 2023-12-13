from django.shortcuts import reverse


def admin_change_url(obj) -> str:
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=(obj.pk,),
    )

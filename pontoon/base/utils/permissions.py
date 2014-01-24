
import commonware.log
import requests

from django.conf import settings
from django.contrib.auth.models import Permission


log = commonware.log.getLogger('pontoon')


def can_localize(user):

    # Grant permission to Mozilla localizers
    url = "https://mozillians.org/api/v1/users/"
    payload = {
        "app_name": "pontoon",
        "app_key": settings.MOZILLIANS_API_KEY,
        "groups": "l10n,localization",
        "format": "json",
        "limit": 2000, # By default, limited to 20
        "is_vouched": True
    }

    log.debug(user.email)

    try:
        r = requests.get(url, params=payload)
        email = user.email

        for l in r.json()["objects"]:
            if email == l["email"]:

                can_localize = Permission.objects.get(codename="can_localize")
                user.user_permissions.add(can_localize)
                log.debug("Permission can_localize set.")

                # Fallback if profile does not allow accessing data
                user.first_name = l.get("full_name", email)
                user.save()
                break;

    except Exception as e:
        log.debug(e)
        log.debug("Is your MOZILLIANS_API_KEY set?")


import commonware.log
import requests

from django.conf import settings
from django.contrib.auth.models import Permission


log = commonware.log.getLogger('pontoon')


def add_can_localize(user):

    # Grant permission to Mozilla localizers
    url = "https://mozillians.org/api/v1/users/"
    payload = {
        "app_name": "pontoon",
        "app_key": settings.MOZILLIANS_API_KEY,
        "groups": "localization",
        "format": "json",
        "limit": 2000, # By default, limited to 20
        "is_vouched": True
    }

    try:
        mozillians = requests.get(url, params=payload)
        email = user.email
        log.debug(email)

        for mozillian in mozillians.json()["objects"]:
            if email == mozillian["email"]:

                can_localize = Permission.objects.get(codename="can_localize")
                user.user_permissions.add(can_localize)
                log.debug("Permission can_localize set.")

                # Fallback if profile does not allow accessing data
                user.first_name = mozillian.get("full_name", email)
                user.save()
                break;

    except Exception as e:
        log.debug(e)
        log.debug("Is your MOZILLIANS_API_KEY set?")

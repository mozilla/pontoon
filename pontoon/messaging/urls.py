from . import views
from django.urls import path


urlpatterns = [
    # Email consent
    path(
        "email-consent/",
        views.email_consent,
        name="pontoon.messaging.email_consent",
    ),
    path(
        "dismiss-email-consent/",
        views.dismiss_email_consent,
        name="pontoon.messaging.dismiss_email_consent",
    ),
    # Unsubscribe
    path(
        "unsubscribe/<uuid:uuid>/",
        views.unsubscribe,
        name="pontoon.messaging.unsubscribe",
    ),
    # Subscribe again
    path(
        "subscribe/<uuid:uuid>/",
        views.subscribe,
        name="pontoon.messaging.subscribe",
    ),
]

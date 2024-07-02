from django.urls import path

from . import views


urlpatterns = [
    # Messaging center
    path(
        "messaging/",
        views.messaging,
        name="pontoon.messaging",
    ),
    path(
        "send-message/",
        views.send_message,
        name="pontoon.messaging.send_message",
    ),
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

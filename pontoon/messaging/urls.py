from django.urls import include, path

from . import views


urlpatterns = [
    # Messaging center
    path(
        "messaging/",
        include(
            [
                # Compose
                path(
                    "",
                    views.messaging,
                    name="pontoon.messaging.compose",
                ),
                # Edit as new
                path(
                    "<int:pk>/",
                    views.messaging,
                    name="pontoon.messaging.edit_as_new",
                ),
                # Sent
                path(
                    "sent/",
                    views.messaging,
                    name="pontoon.messaging.sent",
                ),
                # AJAX views
                path(
                    "ajax/",
                    include(
                        [
                            # Compose
                            path(
                                "",
                                views.ajax_compose,
                                name="pontoon.messaging.ajax.compose",
                            ),
                            # Edit as new
                            path(
                                "<int:pk>/",
                                views.ajax_edit_as_new,
                                name="pontoon.messaging.ajax.edit_as_new",
                            ),
                            # Sent
                            path(
                                "sent/",
                                views.ajax_sent,
                                name="pontoon.messaging.ajax.sent",
                            ),
                            # Send message
                            path(
                                "send/",
                                views.send_message,
                                name="pontoon.messaging.ajax.send_message",
                            ),
                        ]
                    ),
                ),
            ]
        ),
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
